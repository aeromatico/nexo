import React from 'react';

export default function LoadingScreen() {
  return (
    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-primary-600 to-primary-900">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-white border-t-transparent mx-auto mb-4"></div>
        <p className="text-white text-lg font-medium">Cargando...</p>
      </div>
    </div>
  );
}
