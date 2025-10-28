from rest_framework import serializers
from .models import AudioClip, PronunciationFeedback, Dataset, BenchmarkResult
from users.serializers import UserProfileSerializer


class AudioClipSerializer(serializers.ModelSerializer):
    uploader_info = UserProfileSerializer(source='uploader', read_only=True)
    audio_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AudioClip
        fields = [
            'id', 'uploader', 'uploader_info', 'source', 'audio_file', 'audio_url',
            's3_url', 'dialect', 'duration_seconds', 'sample_rate', 'channels',
            'file_size_bytes', 'waveform_data', 'status', 'consent_given',
            'consent_text', 'consent_timestamp', 'asr_draft_transcription',
            'asr_confidence_score', 'final_transcription', 'quality_score',
            'annotation_count', 'consensus_reached', 'consensus_similarity',
            'is_seed_data', 'metadata', 'created_at', 'updated_at', 'validated_at'
        ]
        read_only_fields = [
            'uploader', 'status', 'asr_draft_transcription', 'asr_confidence_score',
            'final_transcription', 'quality_score', 'annotation_count',
            'consensus_reached', 'consensus_similarity', 'validated_at'
        ]
    
    def get_audio_url(self, obj):
        if obj.s3_url:
            return obj.s3_url
        request = self.context.get('request')
        if obj.audio_file and request:
            return request.build_absolute_uri(obj.audio_file.url)
        return None


class AudioClipUploadSerializer(serializers.ModelSerializer):
    audio_file = serializers.FileField()
    
    class Meta:
        model = AudioClip
        fields = [
            'audio_file', 'dialect', 'duration_seconds', 'sample_rate',
            'channels', 'file_size_bytes', 'consent_given', 'consent_text',
            'consent_timestamp', 'source', 'waveform_data', 'metadata'
        ]
    
    def validate_audio_file(self, value):
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("Audio file size cannot exceed 10MB")
        return value
    
    def validate_duration_seconds(self, value):
        if value > 20:
            raise serializers.ValidationError("Audio clip cannot exceed 20 seconds")
        if value < 1:
            raise serializers.ValidationError("Audio clip must be at least 1 second")
        return value
    
    def validate_consent_given(self, value):
        if not value:
            raise serializers.ValidationError("Consent must be given to upload audio")
        return value


class PronunciationFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PronunciationFeedback
        fields = [
            'id', 'audio_clip', 'overall_score', 'clarity_score', 'fluency_score',
            'pronunciation_issues', 'improvement_suggestions', 'phoneme_analysis',
            'created_at'
        ]
        read_only_fields = ['audio_clip']


class DatasetSerializer(serializers.ModelSerializer):
    created_by_info = UserProfileSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'description', 'dialect', 'version', 'created_by',
            'created_by_info', 'total_clips', 'total_duration_seconds',
            'manifest_file', 'metadata', 'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'total_clips', 'total_duration_seconds']


class BenchmarkResultSerializer(serializers.ModelSerializer):
    dataset_info = DatasetSerializer(source='dataset', read_only=True)
    
    class Meta:
        model = BenchmarkResult
        fields = [
            'id', 'dataset', 'dataset_info', 'model_name', 'model_version',
            'wer', 'cer', 'total_clips_tested', 'average_latency_ms',
            'metadata', 'created_at'
        ]


class AudioClipListSerializer(serializers.ModelSerializer):
    uploader_username = serializers.CharField(source='uploader.username', read_only=True)
    uploader_nickname = serializers.CharField(source='uploader.nickname', read_only=True)
    audio_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AudioClip
        fields = [
            'id', 'uploader_username', 'uploader_nickname', 'dialect', 'status',
            'duration_seconds', 'audio_url', 'annotation_count', 'consensus_reached',
            'quality_score', 'created_at'
        ]
    
    def get_audio_url(self, obj):
        if obj.s3_url:
            return obj.s3_url
        request = self.context.get('request')
        if obj.audio_file and request:
            return request.build_absolute_uri(obj.audio_file.url)
        return None
