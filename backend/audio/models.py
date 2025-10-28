from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator, MaxValueValidator
import uuid


class AudioClip(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_annotation', 'In Annotation'),
        ('validated', 'Validated'),
        ('rejected', 'Rejected'),
    ]
    
    DIALECT_CHOICES = [
        ('sheng', 'Sheng'),
        ('kiamu', 'Kiamu'),
        ('kibajuni', 'Kibajuni'),
    ]
    
    SOURCE_CHOICES = [
        ('recording', 'Recording'),
        ('upload', 'Upload'),
        ('seed', 'Seed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='audio_clips')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='recording')
    audio_file = models.FileField(
        upload_to='audio_clips/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['wav', 'mp3', 'ogg', 'webm'])]
    )
    s3_url = models.URLField(blank=True, null=True)
    dialect = models.CharField(max_length=20, choices=DIALECT_CHOICES)
    duration_seconds = models.FloatField(validators=[MaxValueValidator(20.0)])
    sample_rate = models.IntegerField(default=16000)
    channels = models.IntegerField(default=1)
    file_size_bytes = models.BigIntegerField()
    waveform_data = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    consent_given = models.BooleanField(default=False)
    consent_text = models.TextField()
    consent_timestamp = models.DateTimeField()
    asr_draft_transcription = models.TextField(blank=True, null=True)
    asr_confidence_score = models.FloatField(blank=True, null=True)
    final_transcription = models.TextField(blank=True, null=True)
    quality_score = models.FloatField(blank=True, null=True)
    annotation_count = models.IntegerField(default=0)
    consensus_reached = models.BooleanField(default=False)
    consensus_similarity = models.FloatField(blank=True, null=True)
    is_seed_data = models.BooleanField(default=False)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    validated_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'audio_clips'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uploader', 'status']),
            models.Index(fields=['dialect', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.dialect} - {self.id} ({self.status})"
    
    def can_be_deleted_by(self, user):
        return self.uploader == user and self.status in ['pending', 'rejected']
    
    def move_to_annotation_queue(self):
        if self.status == 'pending' and self.consent_given:
            self.status = 'in_annotation'
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False


class PronunciationFeedback(models.Model):
    audio_clip = models.OneToOneField(AudioClip, on_delete=models.CASCADE, related_name='pronunciation_feedback')
    overall_score = models.FloatField()
    clarity_score = models.FloatField()
    fluency_score = models.FloatField()
    pronunciation_issues = models.JSONField(blank=True, null=True)
    improvement_suggestions = models.JSONField(blank=True, null=True)
    phoneme_analysis = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'pronunciation_feedback'
    
    def __str__(self):
        return f"Feedback for {self.audio_clip.id} - Score: {self.overall_score}"


class Dataset(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    dialect = models.CharField(max_length=20, choices=AudioClip.DIALECT_CHOICES)
    version = models.CharField(max_length=50)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    total_clips = models.IntegerField(default=0)
    total_duration_seconds = models.FloatField(default=0.0)
    manifest_file = models.FileField(upload_to='datasets/', blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'datasets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class DatasetClip(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='clips')
    audio_clip = models.ForeignKey(AudioClip, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'dataset_clips'
        unique_together = ['dataset', 'audio_clip']
        ordering = ['order']
    
    def __str__(self):
        return f"{self.dataset.name} - Clip {self.order}"


class BenchmarkResult(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='benchmark_results')
    model_name = models.CharField(max_length=255)
    model_version = models.CharField(max_length=100)
    wer = models.FloatField()
    cer = models.FloatField()
    total_clips_tested = models.IntegerField()
    average_latency_ms = models.FloatField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'benchmark_results'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.model_name} - WER: {self.wer}%"
