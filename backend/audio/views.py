from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from .models import AudioClip, PronunciationFeedback, Dataset, BenchmarkResult
from .serializers import (
    AudioClipSerializer, AudioClipUploadSerializer, AudioClipListSerializer,
    PronunciationFeedbackSerializer, DatasetSerializer, BenchmarkResultSerializer
)
from .tasks import process_audio_clip, generate_pronunciation_feedback
from .utils import generate_waveform_data, upload_to_s3
import logging

logger = logging.getLogger(__name__)


class AudioClipViewSet(viewsets.ModelViewSet):
    queryset = AudioClip.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dialect', 'status', 'uploader']
    search_fields = ['asr_draft_transcription', 'final_transcription']
    ordering_fields = ['created_at', 'duration_seconds', 'quality_score']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AudioClipUploadSerializer
        elif self.action == 'list':
            return AudioClipListSerializer
        return AudioClipSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.action == 'my_clips':
            return queryset.filter(uploader=self.request.user)
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(uploader=self.request.user) | Q(status__in=['in_annotation', 'validated'])
            )
        
        return queryset
    
    def perform_create(self, serializer):
        audio_clip = serializer.save(uploader=self.request.user)
        
        self.request.user.update_streak()
        
        process_audio_clip.delay(str(audio_clip.id))
        generate_pronunciation_feedback.delay(str(audio_clip.id))
        
        logger.info(f"Audio clip {audio_clip.id} created by user {self.request.user.username}")
    
    def destroy(self, request, *args, **kwargs):
        audio_clip = self.get_object()
        
        if not audio_clip.can_be_deleted_by(request.user):
            return Response(
                {'error': 'You can only delete your own pending or rejected clips'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def my_clips(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def feedback(self, request, pk=None):
        audio_clip = self.get_object()
        
        try:
            feedback = PronunciationFeedback.objects.get(audio_clip=audio_clip)
            serializer = PronunciationFeedbackSerializer(feedback)
            return Response(serializer.data)
        except PronunciationFeedback.DoesNotExist:
            return Response(
                {'message': 'Feedback not yet available'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def submit_for_annotation(self, request, pk=None):
        audio_clip = self.get_object()
        
        if audio_clip.uploader != request.user:
            return Response(
                {'error': 'You can only submit your own clips'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if audio_clip.move_to_annotation_queue():
            return Response({
                'message': 'Clip submitted for annotation',
                'clip': AudioClipSerializer(audio_clip, context={'request': request}).data
            })
        else:
            return Response(
                {'error': 'Clip cannot be submitted. Ensure consent is given and status is pending.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dialect', 'is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'total_clips']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(Q(is_public=True) | Q(created_by=self.request.user))
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        dataset = self.get_object()
        
        if not dataset.is_public and dataset.created_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to download this dataset'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if dataset.manifest_file:
            return Response({
                'download_url': request.build_absolute_uri(dataset.manifest_file.url),
                'dataset': DatasetSerializer(dataset).data
            })
        else:
            return Response(
                {'error': 'Dataset manifest not yet generated'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def generate_manifest(self, request, pk=None):
        dataset = self.get_object()
        
        from .tasks import generate_dataset_manifest
        generate_dataset_manifest.delay(dataset.id)
        
        return Response({
            'message': 'Dataset manifest generation started',
            'dataset_id': dataset.id
        })


class BenchmarkResultViewSet(viewsets.ModelViewSet):
    queryset = BenchmarkResult.objects.all()
    serializer_class = BenchmarkResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['dataset', 'model_name']
    ordering_fields = ['wer', 'cer', 'created_at']
    ordering = ['wer']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    user = request.user
    
    total_clips = AudioClip.objects.filter(uploader=user).count()
    pending_clips = AudioClip.objects.filter(uploader=user, status='pending').count()
    in_annotation_clips = AudioClip.objects.filter(uploader=user, status='in_annotation').count()
    validated_clips = AudioClip.objects.filter(uploader=user, status='validated').count()
    
    recent_clips = AudioClip.objects.filter(uploader=user).order_by('-created_at')[:5]
    
    stats = {
        'total_clips': total_clips,
        'pending_clips': pending_clips,
        'in_annotation_clips': in_annotation_clips,
        'validated_clips': validated_clips,
        'recent_clips': AudioClipListSerializer(recent_clips, many=True, context={'request': request}).data,
        'user_stats': {
            'streak_days': user.streak_days,
            'points': user.points,
            'level': user.level,
            'total_earnings': str(user.total_earnings_usdc),
        }
    }
    
    return Response(stats)
