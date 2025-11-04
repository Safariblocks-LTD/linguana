'use client';

import { useRouter } from 'next/navigation';
import { TaskQueue } from '@/components/TaskQueue/TaskQueue';
import { useAuth } from '@/hooks/useAuth';

export default function TasksPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="card max-w-md mx-auto text-center">
          <h2 className="text-2xl font-bold mb-4">Authentication Required</h2>
          <p className="text-muted mb-6">
            Please log in to validate audio clips
          </p>
          <button
            onClick={() => router.push('/auth/login')}
            className="btn-primary"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">Validation Tasks</h1>
          <p className="text-lg text-muted">
            Earn USDC by validating audio transcriptions
          </p>
        </div>

        {/* Info Card */}
        <div className="card bg-gradient-to-br from-primary/10 to-accent/10">
          <h3 className="font-bold text-lg mb-3">How it works</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold mb-2">
                1
              </div>
              <p className="font-semibold mb-1">Listen</p>
              <p className="text-muted">Play the audio clip</p>
            </div>
            <div>
              <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold mb-2">
                2
              </div>
              <p className="font-semibold mb-1">Transcribe</p>
              <p className="text-muted">Verify or correct the text</p>
            </div>
            <div>
              <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold mb-2">
                3
              </div>
              <p className="font-semibold mb-1">Earn</p>
              <p className="text-muted">Get USDC rewards</p>
            </div>
          </div>
        </div>

        {/* Task Queue */}
        <TaskQueue />

        {/* Guidelines */}
        <div className="card bg-bg">
          <h3 className="font-semibold mb-3">Validation Guidelines</h3>
          <ul className="space-y-2 text-sm text-muted">
            <li>• Listen to the entire audio clip before transcribing</li>
            <li>• Transcribe exactly what you hear, including slang and code-switching</li>
            <li>• Use proper spelling and punctuation</li>
            <li>• Tag the languages used (English, Swahili, Sheng)</li>
            <li>• Mark unclear audio appropriately</li>
            <li>• Your validation helps improve AI for Kenyan dialects</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
