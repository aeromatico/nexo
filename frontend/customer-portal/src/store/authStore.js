import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isInitializing: true,

      login: (userData, token) =>
        set({
          user: userData,
          token,
          isInitializing: false,
        }),

      logout: () => {
        set({
          user: null,
          token: null,
        });
        localStorage.removeItem('auth-storage');
      },

      updateUser: (userData) =>
        set({
          user: { ...get().user, ...userData },
        }),

      setToken: (token) =>
        set({ token }),

      initializeAuth: () => {
        // Check if auth data exists in localStorage
        const stored = localStorage.getItem('auth-storage');
        if (stored) {
          try {
            const { state } = JSON.parse(stored);
            set({
              user: state.user,
              token: state.token,
              isInitializing: false,
            });
          } catch (error) {
            console.error('Failed to restore auth:', error);
            set({ isInitializing: false });
          }
        } else {
          set({ isInitializing: false });
        }
      },

      isAuthenticated: () => !!get().token,
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
      }),
    }
  )
);
