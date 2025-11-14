'use client';

import { useState, useEffect } from 'react';
import { Mic, Square, Pause, Play } from 'lucide-react';
import { useMediaRecorder } from '@/hooks/useMediaRecorder';
import { useBackgroundSync } from '@/hooks/useBackgroundSync';
import { generateClipId } from '@/lib/audio';
import { Button } from '@/components/ui/button';

interface AudioRecorderProps {
  dialect?: string;
  maxDuration?: number;
  chunkSize?: number;
  onComplete?: (clipIds: string[]) => void;
}

export function AudioRecorder({
  dialect = 'sheng',
  maxDuration = 20,
  chunkSize = 8,
  onComplete,
}: AudioRecorderProps) {
  const [consent, setConsent] = useState(false);
  const [clipIds, setClipIds] = useState<string[]>([]);
  const { saveClipOffline } = useBackgroundSync();

  const {
    start,
    pause,
    resume,
    stop,
    isRecording,
    isPaused,
    duration,
    error,
  } = useMediaRecorder({
    chunkSize,
    maxDuration,
    onChunkReady: async (chunk) => {
      const clipId = generateClipId();
      
      // Save offline
      await saveClipOffline({
        id: clipId,
        blob: chunk.blob,
        dialect,
        duration: chunk.duration,
        metadata: {
          chunkIndex: clipIds.length,
        },
      });

      setClipIds((prev) => [...prev, clipId]);
    },
    onError: (err) => {
      console.error('Recording error:', err);
    },
  });

  useEffect(() => {
    if (!isRecording && clipIds.length > 0) {
      onComplete?.(clipIds);
    }
  }, [isRecording, clipIds, onComplete]);

  const handleStart = () => {
    if (!consent) {
      alert('Please accept the consent before recording');
      return;
    }
    setClipIds([]);
    start();
  };

  const handleStop = () => {
    stop();
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700 p-8 max-w-2xl mx-auto">
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-2">Record Your Phrase</h2>
          <p className="text-gray-400">Sikika — Rekodi sasa</p>
        </div>

        {/* Consent Checkbox - Moved to top */}
        <div className="flex items-start gap-3 p-4 bg-gray-900/50 rounded-lg border-2 border-[#54e6b6]/30">
          <input
            type="checkbox"
            id="consent"
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
            className="mt-1 w-5 h-5 accent-[#54e6b6]"
          />
          <label htmlFor="consent" className="text-sm text-gray-300 cursor-pointer">
            I consent to having my voice recorded and used for language learning
            purposes. I understand this data will be used to improve speech
            recognition for Kenyan dialects.
          </label>
        </div>

        {/* Waveform Visualization Area */}
        <div className="bg-gray-900/50 rounded-lg p-8 min-h-[200px] flex items-center justify-center">
          {!isRecording && !isPaused && (
            <div className="text-center text-gray-400">
              <Mic className="w-16 h-16 mx-auto mb-4 opacity-50 text-gray-500" />
              <p>Ready to record</p>
            </div>
          )}

          {(isRecording || isPaused) && (
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-4">
                {isRecording && (
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                )}
                <span className="text-3xl font-mono font-bold text-white">
                  {formatTime(duration)}
                </span>
                <span className="text-gray-400">/ {formatTime(maxDuration)}</span>
              </div>

              {/* Simple VU Meter */}
              <div className="w-full max-w-md mx-auto">
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#54e6b6] transition-all duration-100"
                    style={{
                      width: `${Math.min((duration / maxDuration) * 100, 100)}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center justify-center gap-4">
          {!isRecording && !isPaused && (
            <Button
              onClick={handleStart}
              disabled={!consent}
              size="lg"
              className="bg-[#54e6b6] hover:bg-[#54e6b6]/90 text-black font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Start recording"
            >
              <Mic className="w-5 h-5 mr-2" />
              {consent ? 'Start Recording' : 'Accept consent to record'}
            </Button>
          )}

          {isRecording && (
            <>
              <Button
                onClick={pause}
                size="lg"
                variant="outline"
                aria-label="Pause recording"
              >
                <Pause className="w-5 h-5 mr-2" />
                Pause
              </Button>
              <Button
                onClick={handleStop}
                size="lg"
                variant="destructive"
                aria-label="Stop recording"
              >
                <Square className="w-5 h-5 mr-2" />
                Stop
              </Button>
            </>
          )}

          {isPaused && (
            <>
              <Button
                onClick={resume}
                size="lg"
                className="btn-primary"
                aria-label="Resume recording"
              >
                <Play className="w-5 h-5 mr-2" />
                Resume
              </Button>
              <Button
                onClick={handleStop}
                size="lg"
                variant="destructive"
                aria-label="Stop recording"
              >
                <Square className="w-5 h-5 mr-2" />
                Stop
              </Button>
            </>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div
            className="bg-red-500/10 border border-red-500 text-red-400 px-4 py-3 rounded-lg"
            role="alert"
          >
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Info */}
        <div className="text-center text-sm text-gray-500">
          <p>Maximum duration: {maxDuration} seconds</p>
          <p>Audio will be split into {chunkSize}-second chunks</p>
        </div>
      </div>
    </div>
  );
}
