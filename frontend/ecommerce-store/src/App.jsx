import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Layout from '@components/Layout';
import HomePage from '@pages/HomePage';
import ProductListPage from '@pages/ProductListPage';
import ProductDetailPage from '@pages/ProductDetailPage';
import CartPage from '@pages/CartPage';
import CheckoutPage from '@pages/CheckoutPage';
import OrderConfirmationPage from '@pages/OrderConfirmationPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/products" element={<ProductListPage />} />
          <Route path="/products/:id" element={<ProductDetailPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/order-confirmation/:orderId" element={<OrderConfirmationPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
