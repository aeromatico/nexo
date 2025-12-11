import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClientProvider } from '@tanstack/react-query';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import App from './App';
import { queryClient } from './services/queryClient';
import './index.css';

// i18n configuration
import esBoTranslations from './locales/es-BO.json';
import enTranslations from './locales/en.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      'es-BO': { translation: esBoTranslations },
      'en': { translation: enTranslations }
    },
    fallbackLng: 'es-BO',
    interpolation: {
      escapeValue: false
    }
  });

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
