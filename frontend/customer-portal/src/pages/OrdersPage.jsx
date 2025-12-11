import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { orderAPI } from '@services/api';

export default function OrdersPage() {
  const { t } = useTranslation();
  const { data: orders = [], isLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: orderAPI.getOrders,
  });

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
        {t('navigation.orders')}
      </h1>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto" />
        </div>
      ) : orders.length > 0 ? (
        <div className="grid grid-cols-1 gap-4">
          {orders.map((order) => (
            <div key={order.name} className="bg-white dark:bg-slate-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-slate-900 dark:text-white">{order.name}</h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400">{order.customer}</p>
                </div>
                <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium">
                  {order.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white dark:bg-slate-800 rounded-lg">
          <p className="text-slate-600 dark:text-slate-400">{t('common.no_data')}</p>
        </div>
      )}
    </div>
  );
}
