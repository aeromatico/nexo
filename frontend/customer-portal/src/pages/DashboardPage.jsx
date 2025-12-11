import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { dashboardAPI } from '@services/api';
import StatsCard from '@components/Dashboard/StatsCard';
import RecentInvoices from '@components/Dashboard/RecentInvoices';
import OrdersChart from '@components/Dashboard/OrdersChart';

export default function DashboardPage() {
  const { t } = useTranslation();
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardAPI.getDashboardData,
  });

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded w-64 animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">{t('errors.failed_to_load')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
        {t('navigation.dashboard')}
      </h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard
          title={t('dashboard.total_purchases')}
          value={`Bs. ${data?.total_purchases || 0}`}
          trend={data?.purchase_trend}
          icon="shopping-cart"
        />
        <StatsCard
          title={t('dashboard.pending_orders')}
          value={data?.pending_orders || 0}
          trend={data?.order_trend}
          icon="package"
        />
        <StatsCard
          title={t('dashboard.pending_invoices')}
          value={data?.pending_invoices || 0}
          icon="file-text"
        />
        <StatsCard
          title={t('dashboard.open_tickets')}
          value={data?.open_tickets || 0}
          icon="help-circle"
        />
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentInvoices invoices={data?.recent_invoices || []} />
        <OrdersChart data={data?.orders_chart || []} />
      </div>
    </div>
  );
}
