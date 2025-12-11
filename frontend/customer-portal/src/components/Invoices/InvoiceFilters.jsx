import React from 'react';
import { useTranslation } from 'react-i18next';

export default function InvoiceFilters({ filters, onChange }) {
  const { t } = useTranslation();

  const handleStatusChange = (status) => {
    onChange({ ...filters, status });
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-4">
      <div className="flex flex-wrap gap-2">
        {['all', 'draft', 'submitted', 'paid', 'cancelled'].map((status) => (
          <button
            key={status}
            onClick={() => handleStatusChange(status === 'all' ? null : status)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              (!filters.status && status === 'all') || filters.status === status
                ? 'bg-primary-600 text-white'
                : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200'
            }`}
          >
            {t(`filters.${status}`)}
          </button>
        ))}
      </div>
    </div>
  );
}
