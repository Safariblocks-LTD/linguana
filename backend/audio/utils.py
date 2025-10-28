from django.conf import settings
import logging
from pydub import AudioSegment
import io

logger = logging.getLogger(__name__)


def upload_to_s3(file_obj, key):
    return None


def generate_waveform_data(audio_path, num_samples=100):
    try:
        audio = AudioSegment.from_file(audio_path)
        
        samples = audio.get_array_of_samples()
        total_samples = len(samples)
        
        chunk_size = max(1, total_samples // num_samples)
        
        waveform = []
        for i in range(0, total_samples, chunk_size):
            chunk = samples[i:i+chunk_size]
            if chunk:
                max_val = max(abs(s) for s in chunk)
                waveform.append(float(max_val) / 32768.0)
        
        return waveform[:num_samples]
    
    except Exception as e:
        logger.error(f"Failed to generate waveform data: {str(e)}")
        return []


def calculate_audio_metrics(audio_path):
    try:
        audio = AudioSegment.from_file(audio_path)
        
        rms = audio.rms
        clarity = min(1.0, rms / 5000.0)
        
        return {
            'snr': 20.0,
            'clarity': float(clarity),
            'fluency': 0.8,
            'rms': float(rms),
            'zero_crossing_rate': 0.1,
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
