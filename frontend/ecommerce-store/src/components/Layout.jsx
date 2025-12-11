import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { useCartStore } from '@store/cartStore';
import { FiShoppingCart } from 'react-icons/fi';

export default function Layout() {
  const items = useCartStore(state => state.items);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="bg-white dark:bg-slate-900 shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold text-primary-600">
            Nexo Shop
          </Link>
          <nav className="flex items-center gap-8">
            <Link to="/" className="hover:text-primary-600">Inicio</Link>
            <Link to="/products" className="hover:text-primary-600">Productos</Link>
            <Link to="/cart" className="flex items-center gap-2 hover:text-primary-600">
              <FiShoppingCart />
              <span className="bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm">
                {items.length}
              </span>
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-slate-900 border-t mt-12">
        <div className="max-w-6xl mx-auto px-4 py-8 text-center text-slate-600 dark:text-slate-400">
          <p>&copy; 2024 Nexo ERP. Todos los derechos reservados.</p>
        </div>
      </footer>
    </div>
  );
}
