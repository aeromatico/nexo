import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { invoiceAPI } from '@services/api';
import InvoiceCard from '@components/Invoices/InvoiceCard';
import InvoiceFilters from '@components/Invoices/InvoiceFilters';

export default function InvoicesPage() {
  const { t } = useTranslation();
  const [filters, setFilters] = useState({});

  const { data: invoices = [], isLoading } = useQuery({
    queryKey: ['invoices', filters],
    queryFn: () => invoiceAPI.getInvoices(filters),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          {t('navigation.invoices')}
        </h1>
      </div>

      <InvoiceFilters filters={filters} onChange={setFilters} />

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {invoices.length > 0 ? (
            invoices.map((invoice) => (
              <InvoiceCard key={invoice.name} invoice={invoice} />
            ))
          ) : (
            <div className="text-center py-12 bg-white dark:bg-slate-800 rounded-lg">
              <p className="text-slate-600 dark:text-slate-400">
                {t('common.no_data')}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
