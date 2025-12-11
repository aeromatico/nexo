import React, { useEffect } from 'react';
import { useUIStore } from '@store/uiStore';
import { FiX, FiCheckCircle, FiAlertCircle, FiInfo } from 'react-icons/fi';

const iconMap = {
  success: <FiCheckCircle className="text-green-500" />,
  error: <FiAlertCircle className="text-red-500" />,
  info: <FiInfo className="text-blue-500" />,
};

export default function NotificationCenter() {
  const { notifications, removeNotification } = useUIStore();

  return (
    <div className="fixed bottom-4 right-4 space-y-2 z-50 max-w-sm">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className="bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 p-4 flex items-start gap-3 animate-slideInUp"
        >
          {iconMap[notification.type] || iconMap.info}
          <div className="flex-1">
            <p className="font-medium text-slate-900 dark:text-white">
              {notification.title}
            </p>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {notification.message}
            </p>
          </div>
          <button
            onClick={() => removeNotification(notification.id)}
            className="text-slate-400 hover:text-slate-600"
          >
            <FiX size={18} />
          </button>
        </div>
      ))}
    </div>
  );
}
