from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import Levenshtein
import logging
from .models import Annotation, ConsensusResult
from audio.models import AudioClip

logger = logging.getLogger(__name__)


def calculate_normalized_levenshtein_similarity(str1, str2):
    """Calculate normalized Levenshtein similarity (0-100%)"""
    if not str1 or not str2:
        return 0.0
    
    distance = Levenshtein.distance(str1.lower(), str2.lower())
    max_len = max(len(str1), len(str2))
    
    if max_len == 0:
        return 100.0
    
    similarity = (1 - distance / max_len) * 100
    return round(similarity, 2)


def compute_consensus(annotations):
    """Compute consensus from multiple annotations using pairwise similarity"""
    if len(annotations) < settings.REQUIRED_ANNOTATIONS:
        return None, 0.0, {}
    
    transcriptions = [ann.transcription for ann in annotations]
    n = len(transcriptions)
    
    similarity_matrix = {}
    total_similarity = 0
    comparison_count = 0
    
    for i in range(n):
        for j in range(i + 1, n):
            similarity = calculate_normalized_levenshtein_similarity(
                transcriptions[i],
                transcriptions[j]
            )
            similarity_matrix[f"{i}-{j}"] = similarity
            total_similarity += similarity
            comparison_count += 1
    
    if comparison_count == 0:
        return None, 0.0, similarity_matrix
    
    average_similarity = total_similarity / comparison_count
    
    transcription_scores = {}
    for i, trans in enumerate(transcriptions):
        score = 0
        count = 0
        for j in range(n):
            if i != j:
                key = f"{min(i,j)}-{max(i,j)}"
                score += similarity_matrix.get(key, 0)
                count += 1
        transcription_scores[i] = score / count if count > 0 else 0
    
    best_idx = max(transcription_scores, key=transcription_scores.get)
    final_transcription = transcriptions[best_idx]
    
    return final_transcription, average_similarity, similarity_matrix


@shared_task(bind=True, max_retries=3)
def check_consensus_and_reward(self, clip_id):
    """Check if consensus is reached and trigger reward distribution"""
    try:
        with transaction.atomic():
            clip = AudioClip.objects.select_for_update().get(id=clip_id)
            
            annotations = list(clip.annotations.all())
            
            if len(annotations) < settings.REQUIRED_ANNOTATIONS:
                logger.info(f"Clip {clip_id} needs more annotations: {len(annotations)}/{settings.REQUIRED_ANNOTATIONS}")
                return
            
            final_transcription, consensus_score, similarity_matrix = compute_consensus(annotations)
            
            if final_transcription is None:
                logger.error(f"Failed to compute consensus for clip {clip_id}")
                return
            
            consensus_result, created = ConsensusResult.objects.update_or_create(
                clip=clip,
                defaults={
                    'final_transcription': final_transcription,
                    'consensus_score': consensus_score,
                    'annotation_count': len(annotations),
                    'similarity_matrix': similarity_matrix,
                }
            )
            
            if created:
                consensus_result.contributing_annotations.set(annotations)
            
            clip.final_transcription = final_transcription
            clip.consensus_similarity = consensus_score
            
            if consensus_score >= settings.CONSENSUS_THRESHOLD:
                clip.consensus_reached = True
                clip.status = 'validated'
                clip.validated_at = timezone.now()
                
                for ann in annotations:
                    ann.validated = True
                    ann.is_consensus = True
                    ann.save(update_fields=['validated', 'is_consensus'])
                
                clip.uploader.total_contributions += 1
                clip.uploader.save(update_fields=['total_contributions'])
                
                clip.uploader.add_points(10)
                
                from users.utils import check_and_award_badges
                check_and_award_badges(clip.uploader)
                
                from rewards.tasks import create_and_distribute_rewards
                create_and_distribute_rewards.delay(str(clip_id))
                
                logger.info(f"Consensus reached for clip {clip_id}: {consensus_score}%")
            else:
                clip.status = 'in_annotation'
                logger.info(f"Consensus not reached for clip {clip_id}: {consensus_score}% < {settings.CONSENSUS_THRESHOLD}%")
            
            clip.save()
    
    except AudioClip.DoesNotExist:
        logger.error(f"AudioClip {clip_id} not found")
    except Exception as exc:
        logger.error(f"Error checking consensus for clip {clip_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def create_annotation_tasks_for_clip(clip_id):
    """Create annotation tasks for a new clip"""
    try:
        from .models import AnnotationTask
        
        clip = AudioClip.objects.get(id=clip_id)
        
        if clip.status not in ['pending', 'in_annotation']:
            return
        
        existing_tasks = AnnotationTask.objects.filter(clip=clip).count()
        if existing_tasks > 0:
            return
        
        required_annotations = settings.REQUIRED_ANNOTATIONS
        
        for i in range(required_annotations):
            AnnotationTask.objects.create(
                clip=clip,
                priority=1 if clip.is_seed_data else 0
            )
        
        logger.info(f"Created {required_annotations} annotation tasks for clip {clip_id}")
    
    except AudioClip.DoesNotExist:
        logger.error(f"AudioClip {clip_id} not found")
    except Exception as exc:
        logger.error(f"Error creating annotation tasks for clip {clip_id}: {str(exc)}")
