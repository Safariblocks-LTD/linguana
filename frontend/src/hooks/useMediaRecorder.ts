import { useRef, useState, useCallback } from 'react';
import { splitAudioIntoChunks, getAudioDuration, validateAudioConstraints } from '@/lib/audio';

export interface UseMediaRecorderOptions {
  chunkSize?: number; // Duration in seconds for each chunk
  maxDuration?: number; // Maximum recording duration in seconds
  onChunkReady?: (chunk: { blob: Blob; duration: number; id: string }) => void;
  onError?: (error: string) => void;
}

export interface AudioChunkData {
  id: string;
  blob: Blob;
  duration: number;
}

export function useMediaRecorder(options: UseMediaRecorderOptions = {}) {
  const {
    chunkSize = 8,
    maxDuration = 20,
    onChunkReady,
    onError,
  } = options;

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const startTimeRef = useRef<number>(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [duration, setDuration] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const updateDuration = useCallback(() => {
    if (startTimeRef.current) {
      const elapsed = (Date.now() - startTimeRef.current) / 1000;
      setDuration(elapsed);

      if (elapsed >= maxDuration) {
        stop();
      }
    }
  }, [maxDuration]);

  const start = useCallback(async () => {
    try {
      setError(null);
      chunksRef.current = [];

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      streamRef.current = stream;

      // Create MediaRecorder
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm';

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: mimeType });
        
        try {
          // Validate duration
          const audioDuration = await getAudioDuration(audioBlob);
          const validation = validateAudioConstraints(audioDuration, maxDuration);
          
          if (!validation.valid) {
            setError(validation.error || 'Invalid audio');
            onError?.(validation.error || 'Invalid audio');
            return;
          }

          // Split into chunks
          const chunks = await splitAudioIntoChunks(audioBlob, chunkSize);
          
          // Notify about each chunk
          for (const chunk of chunks) {
            onChunkReady?.({
              id: chunk.id,
              blob: chunk.blob,
              duration: chunk.duration,
            });
          }
        } catch (err) {
          const errorMsg = err instanceof Error ? err.message : 'Failed to process audio';
          setError(errorMsg);
          onError?.(errorMsg);
        }
      };

      // Start recording
      mediaRecorder.start(1000); // Collect data every second
      startTimeRef.current = Date.now();
      setIsRecording(true);
      setIsPaused(false);
      setDuration(0);

      // Start duration timer
      timerRef.current = setInterval(updateDuration, 100);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to start recording';
      setError(errorMsg);
      onError?.(errorMsg);
      console.error('Recording error:', err);
    }
  }, [chunkSize, maxDuration, onChunkReady, onError, updateDuration]);

  const pause = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  }, []);

  const resume = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      timerRef.current = setInterval(updateDuration, 100);
    }
  }, [updateDuration]);

  const stop = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }

      // Stop all tracks
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
    }
  }, []);

  const reset = useCallback(() => {
    stop();
    chunksRef.current = [];
    setDuration(0);
    setError(null);
  }, [stop]);

  return {
    start,
    pause,
    resume,
    stop,
    reset,
    isRecording,
    isPaused,
    duration,
    error,
  };
}
