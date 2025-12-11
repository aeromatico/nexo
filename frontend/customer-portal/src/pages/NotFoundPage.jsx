import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="flex items-center justify-center h-screen bg-slate-50 dark:bg-slate-950">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-slate-900 dark:text-white mb-4">404</h1>
        <p className="text-xl text-slate-600 dark:text-slate-400 mb-6">
          Página no encontrada
        </p>
        <Link
          to="/"
          className="inline-block px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
        >
          Volver al inicio
        </Link>
      </div>
    </div>
  );
}
