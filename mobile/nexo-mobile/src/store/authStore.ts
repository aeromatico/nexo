import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isInitializing: true,

      login: (userData: any, token: string) =>
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
        AsyncStorage.removeItem('auth-storage');
      },

      initializeAuth: async () => {
        try {
          const stored = await AsyncStorage.getItem('auth-storage');
          if (stored) {
            const { state } = JSON.parse(stored);
            set({
              user: state.user,
              token: state.token,
              isInitializing: false,
            });
          } else {
            set({ isInitializing: false });
          }
        } catch (error) {
          console.error('Failed to restore auth:', error);
          set({ isInitializing: false });
        }
      },

      isAuthenticated: () => !!get().token,
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
      }),
    }
  )
);
