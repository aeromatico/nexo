import React from 'react';
import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-secondary-600 to-secondary-700 text-white py-20">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-4">Tienda Online Nexo</h1>
          <p className="text-xl opacity-90 mb-8">
            Descubre nuestros productos y servicios
          </p>
          <Link
            to="/products"
            className="inline-block px-8 py-3 bg-white text-secondary-600 font-bold rounded-lg hover:bg-slate-100 transition-colors"
          >
            Explorar Productos
          </Link>
        </div>
      </div>

      {/* Featured Products */}
      <div className="max-w-6xl mx-auto px-4">
        <h2 className="text-3xl font-bold mb-8">Productos Destacados</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Product cards would go here */}
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <p className="text-slate-600">Cargando productos...</p>
          </div>
        </div>
      </div>
    </div>
  );
}
