import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { useAppStore } from '@/stores/useAppStore';

export function useAuth() {
  const { user, isAuthenticated, setUser, logout: storeLogout } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token');
      if (token && !user) {
        try {
          const userData = await api.getCurrentUser();
          setUser(userData);
        } catch (err) {
          // Token invalid, clear it
          localStorage.removeItem('auth_token');
          localStorage.removeItem('refresh_token');
        }
      }
    };

    checkAuth();
  }, [user, setUser]);

  const register = useCallback(
    async (data: { email: string; password: string; username: string }) => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.register(data);
        setUser(response.user);
        return response;
      } catch (err: any) {
        const errorMsg = err.response?.data?.message || 'Registration failed';
        setError(errorMsg);
        throw new Error(errorMsg);
      } finally {
        setLoading(false);
      }
    },
    [setUser]
  );

  const login = useCallback(
    async (data: { email: string; password: string }) => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.login(data);
        setUser(response.user);
        return response;
      } catch (err: any) {
        const errorMsg = err.response?.data?.message || 'Login failed';
        setError(errorMsg);
        throw new Error(errorMsg);
      } finally {
        setLoading(false);
      }
    },
    [setUser]
  );

  const loginWithFirebase = useCallback(
    async (idToken: string) => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.firebaseAuth(idToken);
        setUser(response.user);
        return response;
      } catch (err: any) {
        const errorMsg = err.response?.data?.message || 'Firebase login failed';
        setError(errorMsg);
        throw new Error(errorMsg);
      } finally {
        setLoading(false);
      }
    },
    [setUser]
  );

  const requestMagicLink = useCallback(async (email: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.requestMagicLink(email);
      return response;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || 'Failed to send magic link';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await api.logout();
      storeLogout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setLoading(false);
    }
  }, [storeLogout]);

  const updateProfile = useCallback(
    async (data: any) => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.updateProfile(data);
        setUser(response);
        return response;
      } catch (err: any) {
        const errorMsg = err.response?.data?.message || 'Failed to update profile';
        setError(errorMsg);
        throw new Error(errorMsg);
      } finally {
        setLoading(false);
      }
    },
    [setUser]
  );

  return {
    user,
    isAuthenticated,
    loading,
    error,
    register,
    login,
    loginWithFirebase,
    requestMagicLink,
    logout,
    updateProfile,
  };
}
