'use client';

import { useState, useEffect } from 'react';
import { Save, Tag } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { db } from '@/utils/idb';

interface Segment {
  start: number;
  end: number;
  text: string;
  confidence: number;
}

interface AnnotationEditorProps {
  clipId: string;
  draftText?: string;
  segments?: Segment[];
  onSubmit: (text: string, tags: string[]) => Promise<void>;
}

const AVAILABLE_TAGS = [
  { value: 'en', label: 'English' },
  { value: 'sw', label: 'Swahili' },
  { value: 'sheng', label: 'Sheng' },
  { value: 'code-switch', label: 'Code-switching' },
  { value: 'unclear', label: 'Unclear' },
];

export function AnnotationEditor({
  clipId,
  draftText = '',
  segments = [],
  onSubmit,
}: AnnotationEditorProps) {
  const [text, setText] = useState(draftText);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [consent, setConsent] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // Auto-save draft every 5 seconds
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (text && text !== draftText) {
        try {
          await db.annotationDrafts.put({
            id: clipId,
            clipId,
            draftText: text,
            savedAt: new Date(),
          });
          setLastSaved(new Date());
        } catch (error) {
          console.error('Failed to save draft:', error);
        }
      }
    }, 5000);

    return () => clearTimeout(timer);
  }, [text, clipId, draftText]);

  // Load saved draft on mount
  useEffect(() => {
    const loadDraft = async () => {
      try {
        const draft = await db.annotationDrafts.get(clipId);
        if (draft && draft.draftText) {
          setText(draft.draftText);
          setLastSaved(draft.savedAt);
        }
      } catch (error) {
        console.error('Failed to load draft:', error);
      }
    };

    loadDraft();
  }, [clipId]);

  const handleTagToggle = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const handleSubmit = async () => {
    if (!text.trim()) {
      alert('Please enter transcription text');
      return;
    }

    if (!consent) {
      alert('Please accept the consent before submitting');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(text, selectedTags);
      
      // Clear draft after successful submission
      await db.annotationDrafts.delete(clipId);
    } catch (error) {
      console.error('Submission error:', error);
      alert('Failed to submit annotation. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSegmentClick = (segment: Segment) => {
    // Insert segment text at cursor position
    const textarea = document.querySelector('textarea');
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newText =
        text.substring(0, start) + segment.text + text.substring(end);
      setText(newText);
    }
  };

  return (
    <div className="card space-y-6">
      {/* Segments List */}
      {segments.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-semibold text-sm">ASR Segments (click to insert)</h3>
          <div className="space-y-1">
            {segments.map((segment, index) => (
              <button
                key={index}
                onClick={() => handleSegmentClick(segment)}
                className="w-full text-left px-3 py-2 bg-bg rounded-lg hover:bg-gray-100 transition-colors text-sm"
              >
                <div className="flex justify-between items-start">
                  <span>{segment.text}</span>
                  <span className="text-xs text-muted ml-2">
                    {Math.round(segment.confidence * 100)}%
                  </span>
                </div>
                <div className="text-xs text-muted mt-1">
                  {segment.start.toFixed(1)}s - {segment.end.toFixed(1)}s
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Text Editor */}
      <div className="space-y-2">
        <label htmlFor="transcription" className="font-semibold text-sm block">
          Transcription
        </label>
        <textarea
          id="transcription"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter the transcription here..."
          className="w-full min-h-[150px] px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary resize-y"
          aria-label="Transcription text"
        />
        {lastSaved && (
          <p className="text-xs text-muted">
            Last saved: {lastSaved.toLocaleTimeString()}
          </p>
        )}
      </div>

      {/* Tags */}
      <div className="space-y-2">
        <label className="font-semibold text-sm flex items-center gap-2">
          <Tag className="w-4 h-4" />
          Language Tags
        </label>
        <div className="flex flex-wrap gap-2">
          {AVAILABLE_TAGS.map((tag) => (
            <button
              key={tag.value}
              onClick={() => handleTagToggle(tag.value)}
              className={`px-3 py-1 rounded-full text-sm transition-colors ${
                selectedTags.includes(tag.value)
                  ? 'bg-primary text-white'
                  : 'bg-bg hover:bg-gray-200'
              }`}
            >
              {tag.label}
            </button>
          ))}
        </div>
      </div>

      {/* Consent */}
      <div className="flex items-start gap-3 p-4 bg-bg rounded-lg">
        <input
          type="checkbox"
          id="annotation-consent"
          checked={consent}
          onChange={(e) => setConsent(e.target.checked)}
          className="mt-1"
        />
        <label htmlFor="annotation-consent" className="text-sm">
          I confirm this transcription is accurate to the best of my ability and
          consent to its use for improving speech recognition.
        </label>
      </div>

      {/* Submit Button */}
      <Button
        onClick={handleSubmit}
        disabled={!text.trim() || !consent || isSubmitting}
        className="btn-primary w-full"
        size="lg"
      >
        <Save className="w-5 h-5 mr-2" />
        {isSubmitting ? 'Submitting...' : 'Submit Annotation'}
      </Button>
    </div>
  );
}
