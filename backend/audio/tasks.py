from celery import shared_task
from django.conf import settings
from django.utils import timezone
import requests
import logging
import json
from .models import AudioClip, PronunciationFeedback, Dataset, DatasetClip
from .utils import upload_to_s3, generate_waveform_data, calculate_audio_metrics

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_audio_clip(self, clip_id):
    try:
        audio_clip = AudioClip.objects.get(id=clip_id)
        
        if audio_clip.audio_file:
            s3_url = upload_to_s3(audio_clip.audio_file, f"audio_clips/{clip_id}")
            if s3_url:
                audio_clip.s3_url = s3_url
        
        if not audio_clip.waveform_data:
            waveform_data = generate_waveform_data(audio_clip.audio_file.path)
            audio_clip.waveform_data = waveform_data
        
        audio_clip.save()
        
        request_asr_transcription.delay(clip_id)
        
        logger.info(f"Successfully processed audio clip {clip_id}")
        
    except AudioClip.DoesNotExist:
        logger.error(f"AudioClip {clip_id} not found")
    except Exception as exc:
        logger.error(f"Error processing audio clip {clip_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def request_asr_transcription(self, clip_id):
    try:
        audio_clip = AudioClip.objects.get(id=clip_id)
        
        asr_url = f"{settings.ASR_SERVICE_URL}/transcribe"
        
        files = {'audio': audio_clip.audio_file.open('rb')}
        data = {
            'dialect': audio_clip.dialect,
            'sample_rate': audio_clip.sample_rate
        }
        
        response = requests.post(asr_url, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            audio_clip.asr_draft_transcription = result.get('transcription', '')
            audio_clip.asr_confidence_score = result.get('confidence', 0.0)
            audio_clip.save()
            
            logger.info(f"ASR transcription completed for clip {clip_id}")
        else:
            logger.error(f"ASR service returned status {response.status_code} for clip {clip_id}")
    
    except AudioClip.DoesNotExist:
        logger.error(f"AudioClip {clip_id} not found")
    except requests.exceptions.RequestException as exc:
        logger.error(f"ASR request failed for clip {clip_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=120)
    except Exception as exc:
        logger.error(f"Error requesting ASR for clip {clip_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=2)
def generate_pronunciation_feedback(self, clip_id):
    try:
        audio_clip = AudioClip.objects.get(id=clip_id)
        
        metrics = calculate_audio_metrics(audio_clip.audio_file.path)
        
        overall_score = min(100, max(0, 
            (metrics.get('snr', 20) / 30 * 40) +
            (metrics.get('clarity', 0.7) * 30) +
            (metrics.get('fluency', 0.8) * 30)
        ))
        
        clarity_score = metrics.get('clarity', 0.7) * 100
        fluency_score = metrics.get('fluency', 0.8) * 100
        
        pronunciation_issues = []
        if clarity_score < 60:
            pronunciation_issues.append({
                'type': 'clarity',
                'description': 'Audio clarity could be improved',
                'severity': 'medium'
            })
        
        if fluency_score < 60:
            pronunciation_issues.append({
                'type': 'fluency',
                'description': 'Speech fluency could be improved',
                'severity': 'medium'
            })
        
        improvement_suggestions = []
        if clarity_score < 70:
            improvement_suggestions.append('Try recording in a quieter environment')
            improvement_suggestions.append('Speak closer to the microphone')
        
        if fluency_score < 70:
            improvement_suggestions.append('Practice speaking at a steady pace')
            improvement_suggestions.append('Take a breath between phrases')
        
        PronunciationFeedback.objects.update_or_create(
            audio_clip=audio_clip,
            defaults={
                'overall_score': overall_score,
                'clarity_score': clarity_score,
                'fluency_score': fluency_score,
                'pronunciation_issues': pronunciation_issues,
                'improvement_suggestions': improvement_suggestions,
                'phoneme_analysis': metrics.get('phoneme_data', {})
            }
        )
        
        logger.info(f"Pronunciation feedback generated for clip {clip_id}")
    
    except AudioClip.DoesNotExist:
        logger.error(f"AudioClip {clip_id} not found")
    except Exception as exc:
        logger.error(f"Error generating pronunciation feedback for clip {clip_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def generate_dataset_manifest(dataset_id):
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        
        validated_clips = AudioClip.objects.filter(
            dialect=dataset.dialect,
            status='validated',
            consensus_reached=True
        ).order_by('created_at')
        
        DatasetClip.objects.filter(dataset=dataset).delete()
        
        manifest_data = {
            'dataset_name': dataset.name,
            'version': dataset.version,
            'dialect': dataset.dialect,
            'total_clips': 0,
            'total_duration': 0.0,
            'clips': []
        }
        
        for idx, clip in enumerate(validated_clips):
            DatasetClip.objects.create(
                dataset=dataset,
                audio_clip=clip,
                order=idx
            )
            
            manifest_data['clips'].append({
                'id': str(clip.id),
                'audio_url': clip.s3_url or clip.audio_file.url,
                'transcription': clip.final_transcription,
                'duration': clip.duration_seconds,
                'quality_score': clip.quality_score,
                'dialect': clip.dialect
            })
            
            manifest_data['total_clips'] += 1
            manifest_data['total_duration'] += clip.duration_seconds
        
        dataset.total_clips = manifest_data['total_clips']
        dataset.total_duration_seconds = manifest_data['total_duration']
        
        manifest_filename = f"datasets/{dataset.name.replace(' ', '_')}_v{dataset.version}_manifest.json"
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(manifest_data, f, indent=2)
            temp_path = f.name
        
        from django.core.files import File
        with open(temp_path, 'rb') as f:
            dataset.manifest_file.save(manifest_filename, File(f), save=True)
        
        import os
        os.unlink(temp_path)
        
        logger.info(f"Dataset manifest generated for dataset {dataset_id}")
    
    except Dataset.DoesNotExist:
        logger.error(f"Dataset {dataset_id} not found")
    except Exception as exc:
        logger.error(f"Error generating dataset manifest for {dataset_id}: {str(exc)}")
