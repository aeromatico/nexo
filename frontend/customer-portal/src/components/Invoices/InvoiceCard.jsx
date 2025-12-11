import React from 'react';
import { Link } from 'react-router-dom';
import { FiDownload, FiArrowRight } from 'react-icons/fi';
import StatusBadge from '../Common/StatusBadge';

export default function InvoiceCard({ invoice }) {
  const handleDownload = (e) => {
    e.preventDefault();
    // Trigger PDF download
    console.log('Download PDF:', invoice.name);
  };

  return (
    <Link
      to={`/invoices/${invoice.name}`}
      className="block bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 hover:shadow-lg transition-shadow"
    >
      <div className="p-6 flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">
              {invoice.number}
            </h3>
            <StatusBadge status={invoice.status} />
          </div>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-slate-600 dark:text-slate-400">Cliente</p>
              <p className="font-medium text-slate-900 dark:text-white">
                {invoice.customer_name}
              </p>
            </div>
            <div>
              <p className="text-slate-600 dark:text-slate-400">Fecha</p>
              <p className="font-medium text-slate-900 dark:text-white">
                {new Date(invoice.date).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-slate-600 dark:text-slate-400">Vencimiento</p>
              <p className="font-medium text-slate-900 dark:text-white">
                {new Date(invoice.due_date).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>

        <div className="text-right ml-6">
          <p className="text-2xl font-bold text-slate-900 dark:text-white">
            Bs. {invoice.amount}
          </p>
          <div className="flex gap-2 mt-4">
            <button
              onClick={handleDownload}
              className="p-2 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
              title="Descargar PDF"
            >
              <FiDownload size={20} />
            </button>
            <div className="w-8 h-8 flex items-center justify-center text-primary-600">
              <FiArrowRight size={20} />
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
