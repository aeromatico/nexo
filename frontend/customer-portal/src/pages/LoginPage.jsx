import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '@store/authStore';
import { apiClient } from '@services/api';
import { FiMail, FiLock, FiAlertCircle } from 'react-icons/fi';

export default function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // In a real implementation, this would call your backend auth endpoint
      const response = await apiClient.post('/frappe.auth.login', {
        usr: email,
        pwd: password,
      });

      if (response.message) {
        login(response.message, response.message?.token || 'temp-token');
        navigate('/');
      }
    } catch (err) {
      setError(t('auth.login_failed') || 'Login failed');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-xl p-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
          Nexo ERP
        </h1>
        <p className="text-slate-600 dark:text-slate-400">
          {t('auth.welcome_message') || 'Bienvenido al Portal del Cliente'}
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
          <FiAlertCircle className="text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            {t('auth.email')}
          </label>
          <div className="relative">
            <FiMail className="absolute left-3 top-3 text-slate-400" size={18} />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
              placeholder={t('auth.email_placeholder')}
            />
          </div>
        </div>

        {/* Password */}
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            {t('auth.password')}
          </label>
          <div className="relative">
            <FiLock className="absolute left-3 top-3 text-slate-400" size={18} />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
              placeholder={t('auth.password_placeholder')}
            />
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-slate-400 text-white font-semibold py-2 rounded-lg transition-colors duration-200"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
              {t('auth.logging_in')}
            </span>
          ) : (
            t('auth.login')
          )}
        </button>
      </form>

      {/* Footer */}
      <p className="text-center text-sm text-slate-600 dark:text-slate-400 mt-6">
        {t('auth.need_help')}{' '}
        <a href="#" className="text-primary-600 hover:text-primary-700 font-medium">
          {t('auth.contact_support')}
        </a>
      </p>
    </div>
  );
}
