import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClientProvider } from '@tanstack/react-query';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import App from './App';
import { queryClient } from './services/queryClient';
import './index.css';

i18n
  .use(initReactI18next)
  .init({
    fallbackLng: 'es-BO',
    resources: {
      'es-BO': { translation: {} },
      'en': { translation: {} }
    }
  });

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
