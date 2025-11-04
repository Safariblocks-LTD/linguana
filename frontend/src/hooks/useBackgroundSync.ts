import { useEffect, useCallback } from 'react';
import { db } from '@/utils/idb';
import { api } from '@/lib/api';
import { useAppStore } from '@/stores/useAppStore';

export function useBackgroundSync() {
  const { isOnline, setIsOnline, setPendingUploads } = useAppStore();

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Set initial state
    setIsOnline(navigator.onLine);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [setIsOnline]);

  // Sync pending clips when coming online
  useEffect(() => {
    if (isOnline) {
      syncPendingClips();
    }
  }, [isOnline]);

  const syncPendingClips = useCallback(async () => {
    try {
      const pendingClips = await db.clips
        .where('status')
        .equals('pending')
        .toArray();

      setPendingUploads(pendingClips.length);

      for (const clip of pendingClips) {
        try {
          // Update status to uploading
          await db.clips.update(clip.id, { status: 'uploading' });

          // Create FormData
          const formData = new FormData();
          formData.append('audio_file', clip.blob, `${clip.id}.wav`);
          formData.append('dialect', clip.dialect);
          formData.append('duration', clip.duration.toString());
          
          if (clip.metadata) {
            Object.entries(clip.metadata).forEach(([key, value]) => {
              formData.append(key, String(value));
            });
          }

          // Upload to server
          const response = await api.uploadClip(formData);

          // Update status to uploaded
          await db.clips.update(clip.id, {
            status: 'uploaded',
            serverClipId: response.id,
          });

          const currentPending = await db.clips.where('status').equals('pending').count();
          setPendingUploads(currentPending);
        } catch (error) {
          console.error('Failed to upload clip:', clip.id, error);
          
          // Mark as failed
          await db.clips.update(clip.id, { status: 'failed' });
        }
      }
    } catch (error) {
      console.error('Sync error:', error);
    }
  }, [setPendingUploads]);

  const saveClipOffline = useCallback(
    async (clipData: {
      id: string;
      blob: Blob;
      dialect: string;
      duration: number;
      metadata?: Record<string, any>;
    }) => {
      try {
        await db.clips.add({
          id: clipData.id,
          status: 'pending',
          blob: clipData.blob,
          dialect: clipData.dialect,
          duration: clipData.duration,
          createdAt: new Date(),
          metadata: clipData.metadata || {},
        });

        const currentPending = await db.clips.where('status').equals('pending').count();
        setPendingUploads(currentPending);

        // Try to sync immediately if online
        if (isOnline) {
          syncPendingClips();
        }
      } catch (error) {
        console.error('Failed to save clip offline:', error);
        throw error;
      }
    },
    [isOnline, setPendingUploads, syncPendingClips]
  );

  const retryFailedUploads = useCallback(async () => {
    try {
      const failedClips = await db.clips
        .where('status')
        .equals('failed')
        .toArray();

      // Reset status to pending
      for (const clip of failedClips) {
        await db.clips.update(clip.id, { status: 'pending' });
      }

      // Trigger sync
      await syncPendingClips();
    } catch (error) {
      console.error('Failed to retry uploads:', error);
    }
  }, [syncPendingClips]);

  const clearUploadedClips = useCallback(async () => {
    try {
      await db.clips.where('status').equals('uploaded').delete();
    } catch (error) {
      console.error('Failed to clear uploaded clips:', error);
    }
  }, []);

  return {
    isOnline,
    saveClipOffline,
    syncPendingClips,
    retryFailedUploads,
    clearUploadedClips,
  };
}
