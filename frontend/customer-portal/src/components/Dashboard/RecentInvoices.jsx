import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FiArrowRight } from 'react-icons/fi';
import StatusBadge from '../Common/StatusBadge';

export default function RecentInvoices({ invoices = [] }) {
  const { t } = useTranslation();

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white">
          {t('dashboard.recent_invoices')}
        </h2>
        <Link
          to="/invoices"
          className="flex items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700"
        >
          {t('common.view_all')} <FiArrowRight size={16} />
        </Link>
      </div>

      <div className="space-y-3">
        {invoices.length > 0 ? (
          invoices.map((invoice) => (
            <Link
              key={invoice.name}
              to={`/invoices/${invoice.name}`}
              className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-700 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors"
            >
              <div className="flex-1">
                <p className="font-medium text-slate-900 dark:text-white">
                  {invoice.number}
                </p>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {new Date(invoice.date).toLocaleDateString()}
                </p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-slate-900 dark:text-white">
                  Bs. {invoice.amount}
                </p>
                <StatusBadge status={invoice.status} />
              </div>
            </Link>
          ))
        ) : (
          <p className="text-center text-slate-600 dark:text-slate-400 py-4">
            {t('common.no_data')}
          </p>
        )}
      </div>
    </div>
  );
}
