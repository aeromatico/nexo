import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@store/authStore';

export default function ProtectedRoute() {
  const { token, isInitializing } = useAuthStore();

  if (isInitializing) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return token ? <Outlet /> : <Navigate to="/login" replace />;
}
