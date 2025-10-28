from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count
from .models import Annotation, AnnotationTask, ConsensusResult
from audio.models import AudioClip
from .serializers import (
    AnnotationSerializer, AnnotationCreateSerializer,
    AnnotationTaskSerializer, ConsensusResultSerializer
)
from .tasks import check_consensus_and_reward
import logging

logger = logging.getLogger(__name__)


class AnnotationViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['clip', 'annotator', 'validated', 'quality_rating']
    ordering_fields = ['created_at', 'quality_score']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AnnotationCreateSerializer
        return AnnotationSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(annotator=self.request.user) | Q(clip__uploader=self.request.user)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        annotation = serializer.save(annotator=self.request.user)
        
        clip = annotation.clip
        clip.annotation_count = clip.annotations.count()
        
        if clip.status == 'pending':
            clip.status = 'in_annotation'
        
        clip.save(update_fields=['annotation_count', 'status'])
        
        self.request.user.total_validations += 1
        self.request.user.save(update_fields=['total_validations'])
        
        self.request.user.add_points(5)
        
        if clip.annotation_count >= 3:
            check_consensus_and_reward.delay(str(clip.id))
        
        logger.info(f"Annotation created by {self.request.user.username} for clip {clip.id}")
    
    @action(detail=False, methods=['get'])
    def my_annotations(self, request):
        queryset = self.get_queryset().filter(annotator=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AnnotationTaskViewSet(viewsets.ModelViewSet):
    queryset = AnnotationTask.objects.all()
    serializer_class = AnnotationTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'assigned_to']
    ordering_fields = ['priority', 'created_at']
    ordering = ['-priority', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(assigned_to=self.request.user) | Q(status='pending')
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def next_task(self, request):
        user = request.user
        dialect = request.query_params.get('dialect')
        
        already_annotated_clips = Annotation.objects.filter(
            annotator=user
        ).values_list('clip_id', flat=True)
        
        own_clips = AudioClip.objects.filter(uploader=user).values_list('id', flat=True)
        
        queryset = AnnotationTask.objects.filter(
            status='pending'
        ).exclude(
            clip_id__in=already_annotated_clips
        ).exclude(
            clip_id__in=own_clips
        ).select_related('clip')
        
        if dialect:
            queryset = queryset.filter(clip__dialect=dialect)
        
        task = queryset.first()
        
        if task:
            task.assigned_to = user
            task.status = 'assigned'
            task.assigned_at = timezone.now()
            task.save()
            
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        else:
            return Response(
                {'message': 'No annotation tasks available'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        
        if task.assigned_to != request.user:
            return Response(
                {'error': 'This task is not assigned to you'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        return Response({
            'message': 'Task completed',
            'task': self.get_serializer(task).data
        })
    
    @action(detail=True, methods=['post'])
    def skip(self, request, pk=None):
        task = self.get_object()
        
        if task.assigned_to != request.user:
            return Response(
                {'error': 'This task is not assigned to you'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task.status = 'pending'
        task.assigned_to = None
        task.assigned_at = None
        task.save()
        
        return Response({'message': 'Task skipped'})


class ConsensusResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConsensusResult.objects.all()
    serializer_class = ConsensusResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['clip']
    ordering_fields = ['consensus_score', 'computed_at']
    ordering = ['-computed_at']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def annotation_queue_stats(request):
    dialect = request.query_params.get('dialect')
    
    queryset = AnnotationTask.objects.filter(status='pending')
    
    if dialect:
        queryset = queryset.filter(clip__dialect=dialect)
    
    total_pending = queryset.count()
    
    by_dialect = {}
    for d in ['sheng', 'kiamu', 'kibajuni']:
        count = AnnotationTask.objects.filter(status='pending', clip__dialect=d).count()
        by_dialect[d] = count
    
    user_annotations_today = Annotation.objects.filter(
        annotator=request.user,
        created_at__date=timezone.now().date()
    ).count()
    
    user_total_annotations = request.user.total_validations
    
    stats = {
        'total_pending_tasks': total_pending,
        'by_dialect': by_dialect,
        'user_annotations_today': user_annotations_today,
        'user_total_annotations': user_total_annotations,
    }
    
    return Response(stats)
