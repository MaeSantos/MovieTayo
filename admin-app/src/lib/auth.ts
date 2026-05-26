import { create } from 'zustand';
import { api } from './api';

interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (token: string, remember: boolean) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
}

export const useAuth = create<AuthState>((set) => ({
  isAuthenticated: false,
  token: null,
  isLoading: true,
  error: null,

  login: async (token: string, remember: boolean) => {
    set({ isLoading: true, error: null });

    try {
      // Validate token by fetching stats
      api.setToken(token);
      await api.getStats();

      set({
        isAuthenticated: true,
        token,
        isLoading: false,
        error: null
      });

      if (!remember) {
        // Store in session storage instead
        sessionStorage.setItem('movietayo.admin.token', token);
        localStorage.removeItem('movietayo.admin.token');
      } else {
        localStorage.setItem('movietayo.admin.token', token);
        sessionStorage.removeItem('movietayo.admin.token');
      }
    } catch (error) {
      set({
        isAuthenticated: false,
        token: null,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Authentication failed'
      });
      throw error;
    }
  },

  logout: () => {
    api.clearToken();
    localStorage.removeItem('movietayo.admin.token');
    sessionStorage.removeItem('movietayo.admin.token');
    set({
      isAuthenticated: false,
      token: null,
      error: null
    });
  },

  checkAuth: () => {
    const token = localStorage.getItem('movietayo.admin.token') ||
                  sessionStorage.getItem('movietayo.admin.token');

    if (token) {
      api.setToken(token);
      set({
        isAuthenticated: true,
        token,
        isLoading: false
      });
    } else {
      set({
        isAuthenticated: false,
        token: null,
        isLoading: false
      });
    }
  },
}));

// Initialize auth on load
if (typeof window !== 'undefined') {
  useAuth.getState().checkAuth();
}
