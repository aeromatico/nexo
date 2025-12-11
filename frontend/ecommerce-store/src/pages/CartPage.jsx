import React from 'react';
import { Link } from 'react-router-dom';
import { useCartStore } from '@store/cartStore';

export default function CartPage() {
  const { items, removeItem, updateQuantity } = useCartStore();
  const total = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Carrito de Compras</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Items */}
        <div className="lg:col-span-2">
          {items.length > 0 ? (
            <div className="space-y-4">
              {items.map(item => (
                <div key={item.item_code} className="bg-white rounded-lg p-4 flex justify-between">
                  <div>
                    <h3 className="font-bold">{item.item_name}</h3>
                    <p className="text-slate-600">Bs. {item.price}</p>
                  </div>
                  <div>
                    <input
                      type="number"
                      value={item.quantity}
                      onChange={(e) => updateQuantity(item.item_code, parseInt(e.target.value))}
                      className="w-16 px-2 py-1 border rounded"
                    />
                  </div>
                  <button onClick={() => removeItem(item.item_code)} className="text-red-600 font-bold">
                    Eliminar
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-white rounded-lg">
              <p className="text-slate-600 mb-4">Tu carrito está vacío</p>
              <Link to="/products" className="text-primary-600 font-bold hover:underline">
                Continuar comprando
              </Link>
            </div>
          )}
        </div>

        {/* Summary */}
        <div className="bg-white rounded-lg p-6 h-fit">
          <h2 className="font-bold text-lg mb-4">Resumen</h2>
          <div className="space-y-2 mb-4 border-b pb-4">
            <div className="flex justify-between">
              <span>Subtotal</span>
              <span>Bs. {total}</span>
            </div>
            <div className="flex justify-between">
              <span>Envío</span>
              <span>Bs. 0</span>
            </div>
          </div>
          <div className="flex justify-between font-bold text-lg mb-6">
            <span>Total</span>
            <span>Bs. {total}</span>
          </div>
          <Link
            to="/checkout"
            className="w-full bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-lg font-bold text-center block"
          >
            Proceder al Pago
          </Link>
        </div>
      </div>
    </div>
  );
}
