import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { FiCheckCircle } from 'react-icons/fi';

export default function OrderConfirmationPage() {
  const { orderId } = useParams();

  return (
    <div className="max-w-2xl mx-auto px-4 py-12 text-center">
      <FiCheckCircle className="w-16 h-16 text-green-600 mx-auto mb-6" />
      <h1 className="text-3xl font-bold mb-4">Pedido Confirmado</h1>
      <p className="text-slate-600 mb-4">
        Tu pedido <span className="font-bold">{orderId}</span> ha sido confirmado.
      </p>
      <p className="text-slate-600 mb-8">
        Te enviaremos un email con los detalles pronto.
      </p>
      <div className="space-x-4">
        <Link
          to="/"
          className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg font-bold hover:bg-primary-700"
        >
          Volver al Inicio
        </Link>
        <Link
          to="/products"
          className="inline-block px-6 py-3 bg-slate-200 text-slate-700 rounded-lg font-bold hover:bg-slate-300"
        >
          Continuar Comprando
        </Link>
      </div>
    </div>
  );
}
