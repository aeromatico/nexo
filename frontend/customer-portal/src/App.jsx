import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@store/authStore';

// Layouts
import MainLayout from '@components/Layouts/MainLayout';
import AuthLayout from '@components/Layouts/AuthLayout';

// Pages
import LoginPage from '@pages/LoginPage';
import DashboardPage from '@pages/DashboardPage';
import InvoicesPage from '@pages/InvoicesPage';
import InvoiceDetailPage from '@pages/InvoiceDetailPage';
import OrdersPage from '@pages/OrdersPage';
import OrderDetailPage from '@pages/OrderDetailPage';
import PaymentsPage from '@pages/PaymentsPage';
import SupportPage from '@pages/SupportPage';
import ProfilePage from '@pages/ProfilePage';
import SettingsPage from '@pages/SettingsPage';
import NotFoundPage from '@pages/NotFoundPage';

// Components
import ProtectedRoute from '@components/ProtectedRoute';
import LoadingScreen from '@components/Common/LoadingScreen';

function App() {
  const { user, token, initializeAuth, isInitializing } = useAuthStore();

  useEffect(() => {
    // Initialize auth from localStorage on app load
    initializeAuth();
  }, [initializeAuth]);

  if (isInitializing) {
    return <LoadingScreen />;
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
        </Route>

        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dashboard" element={<Navigate to="/" replace />} />

            {/* Invoices */}
            <Route path="/invoices" element={<InvoicesPage />} />
            <Route path="/invoices/:id" element={<InvoiceDetailPage />} />

            {/* Orders */}
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/orders/:id" element={<OrderDetailPage />} />

            {/* Payments */}
            <Route path="/payments" element={<PaymentsPage />} />

            {/* Support */}
            <Route path="/support" element={<SupportPage />} />

            {/* Profile & Settings */}
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
