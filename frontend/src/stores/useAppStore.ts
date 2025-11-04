import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  username: string;
  wallet_address?: string;
  total_earnings?: number;
  streak_days?: number;
  badges?: any[];
}

interface AppState {
  // User state
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;

  // Recording state
  isRecording: boolean;
  currentDialect: string;
  setIsRecording: (recording: boolean) => void;
  setCurrentDialect: (dialect: string) => void;

  // Upload queue
  pendingUploads: number;
  setPendingUploads: (count: number) => void;
  incrementPendingUploads: () => void;
  decrementPendingUploads: () => void;

  // Offline state
  isOnline: boolean;
  setIsOnline: (online: boolean) => void;

  // Rewards
  pendingRewards: number;
  confirmedRewards: number;
  setPendingRewards: (amount: number) => void;
  setConfirmedRewards: (amount: number) => void;

  // UI state
  showWalletModal: boolean;
  setShowWalletModal: (show: boolean) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // User state
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      logout: () => set({ user: null, isAuthenticated: false }),

      // Recording state
      isRecording: false,
      currentDialect: 'sheng',
      setIsRecording: (recording) => set({ isRecording: recording }),
      setCurrentDialect: (dialect) => set({ currentDialect: dialect }),

      // Upload queue
      pendingUploads: 0,
      setPendingUploads: (count) => set({ pendingUploads: count }),
      incrementPendingUploads: () =>
        set((state) => ({ pendingUploads: state.pendingUploads + 1 })),
      decrementPendingUploads: () =>
        set((state) => ({ pendingUploads: Math.max(0, state.pendingUploads - 1) })),

      // Offline state
      isOnline: true,
      setIsOnline: (online) => set({ isOnline: online }),

      // Rewards
      pendingRewards: 0,
      confirmedRewards: 0,
      setPendingRewards: (amount) => set({ pendingRewards: amount }),
      setConfirmedRewards: (amount) => set({ confirmedRewards: amount }),

      // UI state
      showWalletModal: false,
      setShowWalletModal: (show) => set({ showWalletModal: show }),
    }),
    {
      name: 'linguana-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        currentDialect: state.currentDialect,
      }),
    }
  )
);
