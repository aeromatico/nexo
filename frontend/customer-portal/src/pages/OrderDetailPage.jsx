import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FiArrowLeft } from 'react-icons/fi';

export default function OrderDetailPage() {
  const { t } = useTranslation();
  const { id } = useParams();

  return (
    <div className="p-6 space-y-6">
      <Link to="/orders" className="flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium">
        <FiArrowLeft size={18} />
        Volver a Pedidos
      </Link>

      <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-8">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{id}</h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2">Detalle del Pedido</p>
      </div>
    </div>
  );
}
