import React from 'react';

const statusColors = {
  draft: { bg: 'bg-slate-100 dark:bg-slate-700', text: 'text-slate-700 dark:text-slate-300' },
  submitted: { bg: 'bg-blue-100 dark:bg-blue-900', text: 'text-blue-700 dark:text-blue-300' },
  paid: { bg: 'bg-green-100 dark:bg-green-900', text: 'text-green-700 dark:text-green-300' },
  pending: { bg: 'bg-yellow-100 dark:bg-yellow-900', text: 'text-yellow-700 dark:text-yellow-300' },
  cancelled: { bg: 'bg-red-100 dark:bg-red-900', text: 'text-red-700 dark:text-red-300' },
};

export default function StatusBadge({ status }) {
  const colors = statusColors[status] || statusColors.draft;

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${colors.bg} ${colors.text}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
