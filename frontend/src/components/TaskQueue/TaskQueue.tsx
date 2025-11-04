'use client';

import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { TaskCard } from '@/components/TaskCard/TaskCard';
import { api } from '@/lib/api';

export function TaskQueue() {
  const [currentTask, setCurrentTask] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNextTask = async () => {
    setLoading(true);
    setError(null);
    try {
      const task = await api.getNextTask();
      setCurrentTask(task);
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || 'No tasks available';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNextTask();
  }, []);

  const handleComplete = async (taskId: string, data: { text: string; tags: string[] }) => {
    await api.completeTask(taskId, data);
    
    // Wait a bit to show the success message
    setTimeout(() => {
      fetchNextTask();
    }, 3000);
  };

  const handleSkip = () => {
    fetchNextTask();
  };

  if (loading) {
    return (
      <div className="card text-center py-12">
        <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
        <p className="text-muted">Loading next task...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card text-center py-12">
        <p className="text-lg mb-4">{error}</p>
        <button
          onClick={fetchNextTask}
          className="btn-primary"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!currentTask) {
    return (
      <div className="card text-center py-12">
        <p className="text-lg mb-4">No tasks available at the moment</p>
        <p className="text-sm text-muted mb-4">
          Check back later for more validation tasks
        </p>
        <button
          onClick={fetchNextTask}
          className="btn-primary"
        >
          Refresh
        </button>
      </div>
    );
  }

  return (
    <TaskCard
      task={currentTask}
      onComplete={handleComplete}
      onSkip={handleSkip}
    />
  );
}
