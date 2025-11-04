'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AudioRecorder } from '@/components/AudioRecorder/AudioRecorder';
import { useAuth } from '@/hooks/useAuth';
import { CheckCircle } from 'lucide-react';

const DIALECTS = [
  { value: 'sheng', label: 'Sheng', description: 'Nairobi street language' },
  { value: 'kiamu', label: 'Kiamu', description: 'Lamu dialect' },
  { value: 'kibajuni', label: 'Kibajuni', description: 'Coastal Swahili' },
];

export default function RecordPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [selectedDialect, setSelectedDialect] = useState('sheng');
  const [completed, setCompleted] = useState(false);
  const [clipCount, setClipCount] = useState(0);

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="card max-w-md mx-auto text-center">
          <h2 className="text-2xl font-bold mb-4">Authentication Required</h2>
          <p className="text-muted mb-6">
            Please log in to record audio clips
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

  const handleComplete = (clipIds: string[]) => {
    setClipCount(clipIds.length);
    setCompleted(true);
  };

  if (completed) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="card max-w-md mx-auto text-center py-12">
          <CheckCircle className="w-16 h-16 text-success mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Recording Complete!</h2>
          <p className="text-muted mb-6">
            Successfully recorded {clipCount} clip{clipCount !== 1 ? 's' : ''}
          </p>
          <div className="space-y-3">
            <button
              onClick={() => {
                setCompleted(false);
                setClipCount(0);
              }}
              className="btn-primary w-full"
            >
              Record Another
            </button>
            <button
              onClick={() => router.push('/dashboard')}
              className="btn-secondary w-full"
            >
              Go to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">Record Audio</h1>
          <p className="text-lg text-muted">
            Help build the future of Kenyan dialect recognition
          </p>
        </div>

        {/* Dialect Selection */}
        <div className="card">
          <h2 className="font-bold text-lg mb-4">Select Dialect</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {DIALECTS.map((dialect) => (
              <button
                key={dialect.value}
                onClick={() => setSelectedDialect(dialect.value)}
                className={`p-4 rounded-lg border-2 transition-all text-left ${
                  selectedDialect === dialect.value
                    ? 'border-primary bg-primary/5'
                    : 'border-gray-200 hover:border-primary/50'
                }`}
              >
                <h3 className="font-semibold mb-1">{dialect.label}</h3>
                <p className="text-sm text-muted">{dialect.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Recorder */}
        <AudioRecorder
          dialect={selectedDialect}
          maxDuration={20}
          chunkSize={8}
          onComplete={handleComplete}
        />

        {/* Tips */}
        <div className="card bg-bg">
          <h3 className="font-semibold mb-3">Recording Tips</h3>
          <ul className="space-y-2 text-sm text-muted">
            <li>• Find a quiet environment</li>
            <li>• Speak clearly and naturally</li>
            <li>• Keep your device close to your mouth</li>
            <li>• Maximum recording time: 20 seconds</li>
            <li>• Audio will be automatically split into chunks</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
