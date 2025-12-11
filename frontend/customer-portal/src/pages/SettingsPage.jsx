import React from 'react';
import { useTranslation } from 'react-i18next';

export default function SettingsPage() {
  const { t } = useTranslation();

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
        {t('navigation.settings')}
      </h1>
      <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-8 text-center">
        <p className="text-slate-600 dark:text-slate-400">Configuración - Próximamente</p>
      </div>
    </div>
  );
}
