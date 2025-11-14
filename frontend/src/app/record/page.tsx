'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AudioRecorder } from '@/components/AudioRecorder/AudioRecorder';
import { CheckCircle, Upload, Mic } from 'lucide-react';
import { Button } from '@/components/ui/button';

const DIALECTS = [
  { value: 'sheng', label: 'Sheng', description: 'Nairobi street language' },
  { value: 'kiamu', label: 'Kiamu', description: 'Lamu dialect' },
  { value: 'kibajuni', label: 'Kibajuni', description: 'Coastal Swahili' },
];

export default function RecordPage() {
  const router = useRouter();
  const [selectedDialect, setSelectedDialect] = useState('sheng');
  const [completed, setCompleted] = useState(false);
  const [clipCount, setClipCount] = useState(0);
  const [mode, setMode] = useState<'select' | 'record' | 'upload'>('select');

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

  // Mode selection screen
  if (mode === 'select') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div className="text-center">
              <h1 className="text-4xl font-bold text-white mb-4">Contribute Audio</h1>
              <p className="text-lg text-gray-400">
                Help build the future of Kenyan dialect recognition
              </p>
            </div>

            {/* Dialect Selection */}
            <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700 p-6">
              <h2 className="font-bold text-lg text-white mb-4">Select Dialect</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {DIALECTS.map((dialect) => (
                  <button
                    key={dialect.value}
                    onClick={() => setSelectedDialect(dialect.value)}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      selectedDialect === dialect.value
                        ? 'border-[#54e6b6] bg-[#54e6b6]/10'
                        : 'border-gray-700 hover:border-[#54e6b6]/50 bg-gray-800/50'
                    }`}
                  >
                    <h3 className="font-semibold text-white mb-1">{dialect.label}</h3>
                    <p className="text-sm text-gray-400">{dialect.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Mode Selection */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Record Option */}
              <button
                onClick={() => setMode('record')}
                className="group bg-gradient-to-br from-[#54e6b6]/10 to-transparent border-2 border-[#54e6b6]/30 hover:border-[#54e6b6]/50 rounded-xl p-8 text-left transition-all"
              >
                <div className="flex items-start gap-4">
                  <div className="w-16 h-16 rounded-xl bg-[#54e6b6]/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                    <Mic className="w-8 h-8 text-[#54e6b6]" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-2">Record Audio</h3>
                    <p className="text-gray-400">
                      Record directly from your microphone. Perfect for real-time contributions.
                    </p>
                    <ul className="mt-4 space-y-1 text-sm text-gray-500">
                      <li>• Max 20 seconds</li>
                      <li>• Auto-chunked</li>
                      <li>• Instant upload</li>
                    </ul>
                  </div>
                </div>
              </button>

              {/* Upload Option */}
              <button
                onClick={() => setMode('upload')}
                className="group bg-gradient-to-br from-blue-500/10 to-transparent border-2 border-blue-500/30 hover:border-blue-500/50 rounded-xl p-8 text-left transition-all"
              >
                <div className="flex items-start gap-4">
                  <div className="w-16 h-16 rounded-xl bg-blue-500/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                    <Upload className="w-8 h-8 text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-2">Upload Audio</h3>
                    <p className="text-gray-400">
                      Upload existing audio files. Ideal for pre-recorded content.
                    </p>
                    <ul className="mt-4 space-y-1 text-sm text-gray-500">
                      <li>• MP3, WAV, M4A</li>
                      <li>• Batch upload</li>
                      <li>• Quality check</li>
                    </ul>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Record mode
  if (mode === 'record') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto space-y-8">
            {/* Back button */}
            <Button
              onClick={() => setMode('select')}
              variant="ghost"
              className="text-gray-400 hover:text-white"
            >
              ← Back to options
            </Button>

            {/* Header */}
            <div className="text-center">
              <h1 className="text-4xl font-bold text-white mb-4">Record Audio</h1>
              <p className="text-lg text-gray-400">
                Recording {DIALECTS.find(d => d.value === selectedDialect)?.label}
              </p>
            </div>

            {/* Recorder */}
            <AudioRecorder
              dialect={selectedDialect}
              maxDuration={20}
              chunkSize={8}
              onComplete={handleComplete}
            />

            {/* Tips */}
            <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700 p-6">
              <h3 className="font-semibold text-white mb-3">Recording Tips</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>• Find a quiet environment</li>
                <li>• Speak clearly and naturally</li>
                <li>• Keep your device close to your mouth</li>
                <li>• Maximum recording time: 20 seconds</li>
                <li>• Audio will be automatically split into chunks</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Upload mode
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Back button */}
          <Button
            onClick={() => setMode('select')}
            variant="ghost"
            className="text-gray-400 hover:text-white"
          >
            ← Back to options
          </Button>

          {/* Header */}
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-4">Upload Audio</h1>
            <p className="text-lg text-gray-400">
              Uploading {DIALECTS.find(d => d.value === selectedDialect)?.label}
            </p>
          </div>

          {/* Upload Area */}
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border-2 border-dashed border-gray-700 hover:border-[#54e6b6]/50 transition-colors p-12">
            <div className="text-center">
              <Upload className="w-16 h-16 text-gray-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Drop audio files here</h3>
              <p className="text-gray-400 mb-6">or click to browse</p>
              <input
                type="file"
                accept="audio/*"
                multiple
                className="hidden"
                id="audio-upload"
                onChange={(e) => {
                  // Handle file upload
                  console.log('Files selected:', e.target.files);
                }}
              />
              <label htmlFor="audio-upload">
                <Button className="bg-[#54e6b6] hover:bg-[#54e6b6]/90 text-black">
                  Choose Files
                </Button>
              </label>
              <p className="text-sm text-gray-500 mt-4">
                Supported formats: MP3, WAV, M4A, OGG • Max 10MB per file
              </p>
            </div>
          </div>

          {/* Tips */}
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700 p-6">
            <h3 className="font-semibold text-white mb-3">Upload Tips</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>• Ensure audio is clear and free of background noise</li>
              <li>• Audio should be in the selected dialect</li>
              <li>• Longer files will be automatically chunked</li>
              <li>• You can upload multiple files at once</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
