from django.db import models
from django.conf import settings
from audio.models import AudioClip
import uuid


class Annotation(models.Model):
    QUALITY_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clip = models.ForeignKey(AudioClip, on_delete=models.CASCADE, related_name='annotations')
    annotator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='annotations')
    transcription = models.TextField()
    quality_rating = models.CharField(max_length=20, choices=QUALITY_CHOICES)
    quality_score = models.FloatField(blank=True, null=True)
    confidence_score = models.FloatField(blank=True, null=True)
    time_spent_seconds = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    validated = models.BooleanField(default=False)
    is_consensus = models.BooleanField(default=False)
    similarity_scores = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'annotations'
        unique_together = ['clip', 'annotator']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['clip', 'validated']),
            models.Index(fields=['annotator', 'created_at']),
        ]
    
    def __str__(self):
        return f"Annotation by {self.annotator.username} for clip {self.clip.id}"


class AnnotationTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clip = models.ForeignKey(AudioClip, on_delete=models.CASCADE, related_name='annotation_tasks')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='annotation_tasks',
        blank=True,
        null=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.IntegerField(default=0)
    assigned_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'annotation_tasks'
        ordering = ['-priority', 'created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        return f"Task for clip {self.clip.id} - {self.status}"


class ConsensusResult(models.Model):
    clip = models.OneToOneField(AudioClip, on_delete=models.CASCADE, related_name='consensus_result')
    final_transcription = models.TextField()
    consensus_score = models.FloatField()
    annotation_count = models.IntegerField()
    similarity_matrix = models.JSONField()
    contributing_annotations = models.ManyToManyField(Annotation, related_name='consensus_results')
    computed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consensus_results'
    
    def __str__(self):
        return f"Consensus for clip {self.clip.id} - Score: {self.consensus_score}"
