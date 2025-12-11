import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  FiHome,
  FiFileText,
  FiShoppingCart,
  FiCreditCard,
  FiHelpCircle,
  FiUser,
  FiSettings,
  FiX
} from 'react-icons/fi';

const menuItems = [
  { id: 'dashboard', label: 'navigation.dashboard', icon: FiHome, path: '/' },
  { id: 'invoices', label: 'navigation.invoices', icon: FiFileText, path: '/invoices' },
  { id: 'orders', label: 'navigation.orders', icon: FiShoppingCart, path: '/orders' },
  { id: 'payments', label: 'navigation.payments', icon: FiCreditCard, path: '/payments' },
  { id: 'support', label: 'navigation.support', icon: FiHelpCircle, path: '/support' },
  { id: 'profile', label: 'navigation.profile', icon: FiUser, path: '/profile' },
  { id: 'settings', label: 'navigation.settings', icon: FiSettings, path: '/settings' },
];

export default function Sidebar({ open, onToggle }) {
  const { t } = useTranslation();
  const location = useLocation();

  return (
    <>
      {/* Mobile Overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/50 lg:hidden z-40"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:relative inset-y-0 left-0 z-50 w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 transform transition-transform duration-300 ${
          open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <h1 className="text-xl font-bold text-primary-600">Nexo</h1>
            <button
              onClick={onToggle}
              className="lg:hidden text-slate-500 hover:text-slate-700"
            >
              <FiX size={24} />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto px-4 py-6 space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.id}
                  to={item.path}
                  className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Icon className="mr-3 flex-shrink-0" size={20} />
                  <span className="text-sm font-medium">{t(item.label)}</span>
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="border-t border-slate-200 dark:border-slate-800 px-4 py-4">
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Nexo ERP v1.0.0
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
