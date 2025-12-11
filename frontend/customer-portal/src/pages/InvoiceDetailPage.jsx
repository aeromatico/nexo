import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { invoiceAPI } from '@services/api';
import { FiArrowLeft } from 'react-icons/fi';

export default function InvoiceDetailPage() {
  const { id } = useParams();
  const { data: invoice, isLoading } = useQuery({
    queryKey: ['invoice', id],
    queryFn: () => invoiceAPI.getInvoiceDetail(id),
  });

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="h-96 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <Link to="/invoices" className="flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium">
        <FiArrowLeft size={18} />
        Volver a Facturas
      </Link>

      <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-8">
        {/* Invoice Header */}
        <div className="grid grid-cols-2 gap-8 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
              {invoice?.number}
            </h1>
            <p className="text-slate-600 dark:text-slate-400">{invoice?.customer_name}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-600 dark:text-slate-400">Fecha</p>
            <p className="text-lg font-semibold text-slate-900 dark:text-white">
              {new Date(invoice?.date).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Invoice Items */}
        <div className="mb-8">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Detalles</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-700">
                  <th className="text-left px-4 py-2 font-semibold">Concepto</th>
                  <th className="text-right px-4 py-2 font-semibold">Cantidad</th>
                  <th className="text-right px-4 py-2 font-semibold">Precio</th>
                  <th className="text-right px-4 py-2 font-semibold">Total</th>
                </tr>
              </thead>
              <tbody>
                {invoice?.items?.map((item, idx) => (
                  <tr key={idx} className="border-b border-slate-200 dark:border-slate-700">
                    <td className="px-4 py-3">{item.description}</td>
                    <td className="text-right px-4 py-3">{item.quantity}</td>
                    <td className="text-right px-4 py-3">Bs. {item.rate}</td>
                    <td className="text-right px-4 py-3 font-semibold">Bs. {item.amount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Totals */}
        <div className="flex justify-end mb-8">
          <div className="w-80">
            <div className="flex justify-between py-2 border-b border-slate-200 dark:border-slate-700">
              <span>Subtotal</span>
              <span>Bs. {invoice?.subtotal}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-200 dark:border-slate-700">
              <span>IVA (13%)</span>
              <span>Bs. {invoice?.tax}</span>
            </div>
            <div className="flex justify-between py-3 text-lg font-bold">
              <span>Total</span>
              <span>Bs. {invoice?.amount}</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button className="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors">
            Descargar PDF
          </button>
          <button className="px-6 py-2 bg-secondary-600 hover:bg-secondary-700 text-white rounded-lg font-medium transition-colors">
            Pagar Ahora
          </button>
        </div>
      </div>
    </div>
  );
}
