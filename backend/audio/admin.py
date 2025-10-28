from django.contrib import admin
from .models import AudioClip, PronunciationFeedback, Dataset, DatasetClip, BenchmarkResult


@admin.register(AudioClip)
class AudioClipAdmin(admin.ModelAdmin):
    list_display = ['id', 'uploader', 'dialect', 'status', 'duration_seconds', 'annotation_count', 'consensus_reached', 'created_at']
    list_filter = ['status', 'dialect', 'consensus_reached', 'is_seed_data']
    search_fields = ['id', 'uploader__username', 'asr_draft_transcription', 'final_transcription']
    readonly_fields = ['id', 'created_at', 'updated_at', 'validated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'uploader', 'source', 'dialect', 'status')
        }),
        ('Audio File', {
            'fields': ('audio_file', 's3_url', 'duration_seconds', 'sample_rate', 'channels', 'file_size_bytes')
        }),
        ('Consent', {
            'fields': ('consent_given', 'consent_text', 'consent_timestamp')
        }),
        ('Transcription', {
            'fields': ('asr_draft_transcription', 'asr_confidence_score', 'final_transcription')
        }),
        ('Validation', {
            'fields': ('annotation_count', 'consensus_reached', 'consensus_similarity', 'quality_score')
        }),
        ('Metadata', {
            'fields': ('is_seed_data', 'waveform_data', 'metadata', 'created_at', 'updated_at', 'validated_at')
        }),
    )


@admin.register(PronunciationFeedback)
class PronunciationFeedbackAdmin(admin.ModelAdmin):
    list_display = ['audio_clip', 'overall_score', 'clarity_score', 'fluency_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['audio_clip__id']


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'dialect', 'total_clips', 'total_duration_seconds', 'is_public', 'created_at']
    list_filter = ['dialect', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['total_clips', 'total_duration_seconds', 'created_at', 'updated_at']


@admin.register(DatasetClip)
class DatasetClipAdmin(admin.ModelAdmin):
    list_display = ['dataset', 'audio_clip', 'order']
    list_filter = ['dataset']
    search_fields = ['dataset__name', 'audio_clip__id']


@admin.register(BenchmarkResult)
class BenchmarkResultAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'model_version', 'dataset', 'wer', 'cer', 'total_clips_tested', 'created_at']
    list_filter = ['model_name', 'created_at']
    search_fields = ['model_name', 'model_version']
    readonly_fields = ['created_at']
