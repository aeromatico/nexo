import { create } from 'zustand';

export const useUIStore = create((set) => ({
  sidebarOpen: true,
  darkMode: localStorage.getItem('theme') === 'dark',
  language: localStorage.getItem('language') || 'es-BO',
  notifications: [],

  toggleSidebar: () =>
    set((state) => ({
      sidebarOpen: !state.sidebarOpen,
    })),

  setDarkMode: (isDark) => {
    set({ darkMode: isDark });
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  },

  setLanguage: (lang) => {
    set({ language: lang });
    localStorage.setItem('language', lang);
  },

  addNotification: (notification) =>
    set((state) => ({
      notifications: [...state.notifications, { ...notification, id: Date.now() }],
    })),

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),

  clearNotifications: () =>
    set({ notifications: [] }),
}));
