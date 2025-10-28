from django.contrib import admin
from .models import Annotation, AnnotationTask, ConsensusResult


@admin.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = ['id', 'clip', 'annotator', 'quality_rating', 'validated', 'is_consensus', 'created_at']
    list_filter = ['validated', 'is_consensus', 'quality_rating', 'created_at']
    search_fields = ['clip__id', 'annotator__username', 'transcription']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AnnotationTask)
class AnnotationTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'clip', 'assigned_to', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['clip__id', 'assigned_to__username']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ConsensusResult)
class ConsensusResultAdmin(admin.ModelAdmin):
    list_display = ['clip', 'consensus_score', 'annotation_count', 'computed_at']
    list_filter = ['computed_at']
    search_fields = ['clip__id', 'final_transcription']
    readonly_fields = ['computed_at']
