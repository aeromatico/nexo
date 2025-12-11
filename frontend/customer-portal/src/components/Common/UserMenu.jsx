import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FiLogOut, FiSettings } from 'react-icons/fi';

export default function UserMenu({ user, onLogout, onClose }) {
  const { t } = useTranslation();

  return (
    <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 z-50">
      {/* User Info */}
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-700">
        <p className="text-sm font-medium text-slate-900 dark:text-white">
          {user?.full_name || user?.name}
        </p>
        <p className="text-xs text-slate-500 dark:text-slate-400">{user?.email}</p>
      </div>

      {/* Menu Items */}
      <Link
        to="/settings"
        className="block px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center gap-2"
        onClick={onClose}
      >
        <FiSettings size={16} />
        {t('navigation.settings')}
      </Link>

      {/* Logout */}
      <button
        onClick={onLogout}
        className="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-slate-700 flex items-center gap-2 border-t border-slate-200 dark:border-slate-700"
      >
        <FiLogOut size={16} />
        {t('auth.logout')}
      </button>
    </div>
  );
}
