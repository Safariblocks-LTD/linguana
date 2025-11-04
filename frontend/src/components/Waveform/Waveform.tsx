'use client';

import { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, SkipBack, SkipForward } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface WaveformProps {
  audioUrl?: string;
  blob?: Blob;
  onSeek?: (time: number) => void;
  playbackRate?: number;
}

export function Waveform({
  audioUrl,
  blob,
  onSeek,
  playbackRate = 1,
}: WaveformProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    if (!containerRef.current) return;

    // Initialize WaveSurfer
    const wavesurfer = WaveSurfer.create({
      container: containerRef.current,
      waveColor: '#6B7280',
      progressColor: '#40E0D0',
      cursorColor: '#FF9F42',
      barWidth: 2,
      barRadius: 3,
      cursorWidth: 2,
      height: 80,
      barGap: 2,
    });

    wavesurferRef.current = wavesurfer;

    // Load audio
    if (audioUrl) {
      wavesurfer.load(audioUrl);
    } else if (blob) {
      wavesurfer.loadBlob(blob);
    }

    // Event listeners
    wavesurfer.on('ready', () => {
      setDuration(wavesurfer.getDuration());
    });

    wavesurfer.on('play', () => setIsPlaying(true));
    wavesurfer.on('pause', () => setIsPlaying(false));

    wavesurfer.on('audioprocess', () => {
      setCurrentTime(wavesurfer.getCurrentTime());
    });

    wavesurfer.on('interaction', () => {
      const time = wavesurfer.getCurrentTime();
      setCurrentTime(time);
      onSeek?.(time);
    });

    return () => {
      wavesurfer.destroy();
    };
  }, [audioUrl, blob, onSeek]);

  useEffect(() => {
    if (wavesurferRef.current) {
      wavesurferRef.current.setPlaybackRate(playbackRate);
    }
  }, [playbackRate]);

  const togglePlayPause = () => {
    wavesurferRef.current?.playPause();
  };

  const skipBackward = () => {
    if (wavesurferRef.current) {
      const newTime = Math.max(0, currentTime - 5);
      wavesurferRef.current.seekTo(newTime / duration);
    }
  };

  const skipForward = () => {
    if (wavesurferRef.current) {
      const newTime = Math.min(duration, currentTime + 5);
      wavesurferRef.current.seekTo(newTime / duration);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-4">
      {/* Waveform Container */}
      <div
        ref={containerRef}
        className="bg-bg rounded-lg p-4"
        role="region"
        aria-label="Audio waveform"
      />

      {/* Time Display */}
      <div className="flex justify-between text-sm text-muted">
        <span>{formatTime(currentTime)}</span>
        <span>{formatTime(duration)}</span>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-2">
        <Button
          onClick={skipBackward}
          variant="outline"
          size="sm"
          aria-label="Skip backward 5 seconds"
        >
          <SkipBack className="w-4 h-4" />
        </Button>

        <Button
          onClick={togglePlayPause}
          size="lg"
          className="btn-primary"
          aria-label={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? (
            <Pause className="w-5 h-5" />
          ) : (
            <Play className="w-5 h-5" />
          )}
        </Button>

        <Button
          onClick={skipForward}
          variant="outline"
          size="sm"
          aria-label="Skip forward 5 seconds"
        >
          <SkipForward className="w-4 h-4" />
        </Button>
      </div>

      {/* Keyboard Instructions */}
      <div className="text-xs text-center text-muted">
        <p>Keyboard: Space to play/pause, ← → to seek</p>
      </div>
    </div>
  );
}
