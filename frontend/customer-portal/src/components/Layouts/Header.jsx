import React, { useState } from 'react';
import { useAuthStore } from '@store/authStore';
import { useUIStore } from '@store/uiStore';
import { FiMenu, FiBell, FiMoon, FiSun, FiLogOut } from 'react-icons/fi';
import UserMenu from '../Common/UserMenu';

export default function Header({ onToggleSidebar }) {
  const { user, logout } = useAuthStore();
  const { darkMode, setDarkMode } = useUIStore();
  const [showUserMenu, setShowUserMenu] = useState(false);

  return (
    <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
      <div className="px-6 py-4 flex items-center justify-between">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg"
        >
          <FiMenu size={24} />
        </button>

        <div className="flex-1" />

        <div className="flex items-center gap-4">
          {/* Notifications */}
          <button className="relative p-2 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg">
            <FiBell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
          </button>

          {/* Theme Toggle */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg"
          >
            {darkMode ? <FiSun size={20} /> : <FiMoon size={20} />}
          </button>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                {user?.name?.charAt(0).toUpperCase() || 'U'}
              </div>
            </button>

            {showUserMenu && (
              <UserMenu
                user={user}
                onLogout={() => {
                  logout();
                  window.location.href = '/login';
                }}
                onClose={() => setShowUserMenu(false)}
              />
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
