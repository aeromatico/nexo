import React from 'react';
import { useParams } from 'react-router-dom';
import { useCartStore } from '@store/cartStore';

export default function ProductDetailPage() {
  const { id } = useParams();
  const { addItem } = useCartStore();

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="grid grid-cols-2 gap-8">
        {/* Product Image */}
        <div className="bg-slate-100 rounded-lg h-96"></div>

        {/* Product Info */}
        <div>
          <h1 className="text-3xl font-bold mb-2">Producto: {id}</h1>
          <div className="space-y-4">
            <button className="w-full bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-lg font-bold">
              Agregar al Carrito
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
