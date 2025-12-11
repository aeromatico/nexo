import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartStore } from '@store/cartStore';

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { items, clearCart } = useCartStore();
  const [step, setStep] = useState(1); // 1: Shipping, 2: Payment, 3: Confirmation
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    address: '',
    phone: ''
  });

  const handleSubmit = () => {
    if (step === 2) {
      // Process payment
      const orderId = 'ORD-' + Date.now();
      clearCart();
      navigate(`/order-confirmation/${orderId}`);
    } else {
      setStep(step + 1);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Checkout</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Checkout Form */}
        <div className="lg:col-span-2 space-y-6">
          {step === 1 && (
            <div className="bg-white rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4">Información de Envío</h2>
              {/* Form fields */}
              <button
                onClick={handleSubmit}
                className="w-full bg-primary-600 text-white py-2 rounded font-bold"
              >
                Continuar
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="bg-white rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4">Método de Pago</h2>
              {/* Payment options */}
              <button
                onClick={handleSubmit}
                className="w-full bg-primary-600 text-white py-2 rounded font-bold"
              >
                Completar Pedido
              </button>
            </div>
          )}
        </div>

        {/* Order Summary */}
        <div className="bg-white rounded-lg p-6 h-fit">
          <h2 className="font-bold text-lg mb-4">Resumen del Pedido</h2>
          <div className="space-y-2 mb-4">
            {items.map(item => (
              <div key={item.item_code} className="flex justify-between text-sm">
                <span>{item.item_name} x{item.quantity}</span>
                <span>Bs. {item.price * item.quantity}</span>
              </div>
            ))}
          </div>
          <div className="border-t pt-4 flex justify-between font-bold">
            <span>Total</span>
            <span>Bs. {items.reduce((sum, item) => sum + (item.price * item.quantity), 0)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
