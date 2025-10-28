from rest_framework import serializers
from .models import Annotation, AnnotationTask, ConsensusResult
from audio.serializers import AudioClipListSerializer
from users.serializers import UserProfileSerializer


class AnnotationSerializer(serializers.ModelSerializer):
    annotator_info = UserProfileSerializer(source='annotator', read_only=True)
    clip_info = AudioClipListSerializer(source='clip', read_only=True)
    
    class Meta:
        model = Annotation
        fields = [
            'id', 'clip', 'clip_info', 'annotator', 'annotator_info',
            'transcription', 'quality_rating', 'quality_score', 'confidence_score',
            'time_spent_seconds', 'notes', 'validated', 'is_consensus',
            'similarity_scores', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'annotator', 'validated', 'is_consensus', 'similarity_scores',
            'quality_score'
        ]


class AnnotationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = [
            'clip', 'transcription', 'quality_rating', 'confidence_score',
            'time_spent_seconds', 'notes'
        ]
    
    def validate(self, attrs):
        clip = attrs.get('clip')
        user = self.context['request'].user
        
        if Annotation.objects.filter(clip=clip, annotator=user).exists():
            raise serializers.ValidationError("You have already annotated this clip")
        
        if clip.uploader == user:
            raise serializers.ValidationError("You cannot annotate your own clip")
        
        if clip.status not in ['in_annotation', 'pending']:
            raise serializers.ValidationError("This clip is not available for annotation")
        
        return attrs


class AnnotationTaskSerializer(serializers.ModelSerializer):
    clip_info = AudioClipListSerializer(source='clip', read_only=True)
    assigned_to_info = UserProfileSerializer(source='assigned_to', read_only=True)
    
    class Meta:
        model = AnnotationTask
        fields = [
            'id', 'clip', 'clip_info', 'assigned_to', 'assigned_to_info',
            'status', 'priority', 'assigned_at', 'completed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['assigned_to', 'assigned_at', 'completed_at']


class ConsensusResultSerializer(serializers.ModelSerializer):
    clip_info = AudioClipListSerializer(source='clip', read_only=True)
    contributing_annotations_data = AnnotationSerializer(source='contributing_annotations', many=True, read_only=True)
    
    class Meta:
        model = ConsensusResult
        fields = [
            'id', 'clip', 'clip_info', 'final_transcription', 'consensus_score',
            'annotation_count', 'similarity_matrix', 'contributing_annotations',
            'contributing_annotations_data', 'computed_at'
        ]
