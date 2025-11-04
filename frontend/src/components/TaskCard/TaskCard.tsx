'use client';

import { useState } from 'react';
import { CheckCircle, XCircle } from 'lucide-react';
import { Waveform } from '@/components/Waveform/Waveform';
import { AnnotationEditor } from '@/components/AnnotationEditor/AnnotationEditor';
import * as confetti from 'canvas-confetti';

interface Task {
  id: string;
  clip: {
    id: string;
    audio_url: string;
    dialect: string;
    duration: number;
  };
  asr_draft?: string;
  segments?: Array<{
    start: number;
    end: number;
    text: string;
    confidence: number;
  }>;
  tokens_pending?: number;
}

interface TaskCardProps {
  task: Task;
  onComplete: (taskId: string, data: { text: string; tags: string[] }) => Promise<void>;
  onSkip?: () => void;
}

export function TaskCard({ task, onComplete, onSkip }: TaskCardProps) {
  const [completed, setCompleted] = useState(false);
  const [reward, setReward] = useState<number | null>(null);

  const handleSubmit = async (text: string, tags: string[]) => {
    await onComplete(task.id, { text, tags });
    
    // Show reward
    const rewardAmount = task.tokens_pending || 0.02;
    setReward(rewardAmount);
    setCompleted(true);

    // Celebrate with confetti
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#40E0D0', '#FF9F42'],
    });
  };

  if (completed) {
    return (
      <div className="card text-center py-12">
        <CheckCircle className="w-16 h-16 text-success mx-auto mb-4" />
        <h3 className="text-2xl font-bold mb-2">Thank you!</h3>
        <p className="text-lg mb-4">
          You earned <span className="font-bold text-primary">${reward?.toFixed(2)} USDC</span> pending
        </p>
        <p className="text-sm text-muted">
          Your reward will be confirmed once consensus is reached
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Task Info */}
      <div className="card">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="font-bold text-lg">Validation Task</h3>
            <p className="text-sm text-muted">
              Dialect: <span className="capitalize">{task.clip.dialect}</span> •
              Duration: {task.clip.duration.toFixed(1)}s
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-muted">Reward</p>
            <p className="font-bold text-primary">
              ${(task.tokens_pending || 0.02).toFixed(2)} USDC
            </p>
          </div>
        </div>

        {/* Audio Player */}
        <Waveform audioUrl={task.clip.audio_url} />
      </div>

      {/* Annotation Editor */}
      <AnnotationEditor
        clipId={task.clip.id}
        draftText={task.asr_draft}
        segments={task.segments}
        onSubmit={handleSubmit}
      />

      {/* Skip Button */}
      {onSkip && (
        <button
          onClick={onSkip}
          className="w-full text-center text-sm text-muted hover:text-primary transition-colors"
        >
          Skip this task
        </button>
      )}
    </div>
  );
}
