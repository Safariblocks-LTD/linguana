import boto3
from django.conf import settings
import numpy as np
import wave
import logging
from pydub import AudioSegment
import io

logger = logging.getLogger(__name__)


def upload_to_s3(file_obj, key):
    if not settings.AWS_STORAGE_BUCKET_NAME:
        return None
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        file_obj.seek(0)
        
        s3_client.upload_fileobj(
            file_obj,
            settings.AWS_STORAGE_BUCKET_NAME,
            key,
            ExtraArgs={'ContentType': 'audio/wav'}
        )
        
        url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{key}"
        
        logger.info(f"File uploaded to S3: {key}")
        return url
    
    except Exception as e:
        logger.error(f"Failed to upload to S3: {str(e)}")
        return None


def generate_waveform_data(audio_path, num_samples=100):
    try:
        audio = AudioSegment.from_file(audio_path)
        
        samples = np.array(audio.get_array_of_samples())
        
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)
        
        samples = samples.astype(float)
        samples = samples / np.max(np.abs(samples))
        
        chunk_size = len(samples) // num_samples
        if chunk_size == 0:
            chunk_size = 1
        
        waveform = []
        for i in range(0, len(samples), chunk_size):
            chunk = samples[i:i+chunk_size]
            if len(chunk) > 0:
                waveform.append(float(np.max(np.abs(chunk))))
        
        return waveform[:num_samples]
    
    except Exception as e:
        logger.error(f"Failed to generate waveform data: {str(e)}")
        return []


def calculate_audio_metrics(audio_path):
    try:
        audio = AudioSegment.from_file(audio_path)
        
        samples = np.array(audio.get_array_of_samples())
        
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)
        
        samples = samples.astype(float)
        
        signal_power = np.mean(samples ** 2)
        noise_power = np.var(samples)
        
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
        else:
            snr = 30.0
        
        rms = np.sqrt(np.mean(samples ** 2))
        clarity = min(1.0, rms / 5000.0)
        
        zero_crossings = np.sum(np.diff(np.sign(samples)) != 0)
        zcr = zero_crossings / len(samples)
        fluency = 1.0 - min(1.0, zcr * 10)
        
        return {
            'snr': float(snr),
            'clarity': float(clarity),
            'fluency': float(fluency),
            'rms': float(rms),
            'zero_crossing_rate': float(zcr),
            'phoneme_data': {}
        }
    
    except Exception as e:
        logger.error(f"Failed to calculate audio metrics: {str(e)}")
        return {
            'snr': 20.0,
            'clarity': 0.7,
            'fluency': 0.8,
            'phoneme_data': {}
        }


def convert_audio_to_wav(input_path, output_path, sample_rate=16000, channels=1):
    try:
        audio = AudioSegment.from_file(input_path)
        
        audio = audio.set_frame_rate(sample_rate)
        audio = audio.set_channels(channels)
        audio = audio.set_sample_width(2)
        
        audio.export(output_path, format='wav')
        
        logger.info(f"Audio converted to WAV: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to convert audio to WAV: {str(e)}")
        return False


def chunk_audio(audio_path, chunk_duration_seconds=8):
    try:
        audio = AudioSegment.from_file(audio_path)
        
        chunk_length_ms = chunk_duration_seconds * 1000
        
        chunks = []
        for i in range(0, len(audio), chunk_length_ms):
            chunk = audio[i:i+chunk_length_ms]
            chunks.append(chunk)
        
        return chunks
    
    except Exception as e:
        logger.error(f"Failed to chunk audio: {str(e)}")
        return []


def validate_audio_quality(audio_path):
    try:
        metrics = calculate_audio_metrics(audio_path)
        
        issues = []
        
        if metrics['snr'] < 10:
            issues.append('Audio has too much background noise')
        
        if metrics['clarity'] < 0.3:
            issues.append('Audio clarity is too low')
        
        if metrics['rms'] < 500:
            issues.append('Audio volume is too low')
        
        audio = AudioSegment.from_file(audio_path)
        if len(audio) < 1000:
            issues.append('Audio is too short (minimum 1 second)')
        
        if len(audio) > 20000:
            issues.append('Audio is too long (maximum 20 seconds)')
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'metrics': metrics
        }
    
    except Exception as e:
        logger.error(f"Failed to validate audio quality: {str(e)}")
        return {
            'is_valid': False,
            'issues': ['Failed to analyze audio file'],
            'metrics': {}
        }
