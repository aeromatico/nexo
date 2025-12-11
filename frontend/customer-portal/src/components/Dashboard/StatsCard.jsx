import React from 'react';
import {
  FiShoppingCart,
  FiPackage,
  FiFileText,
  FiHelpCircle,
  FiTrendingUp,
  FiTrendingDown
} from 'react-icons/fi';

const iconMap = {
  'shopping-cart': FiShoppingCart,
  'package': FiPackage,
  'file-text': FiFileText,
  'help-circle': FiHelpCircle,
};

export default function StatsCard({ title, value, trend, icon }) {
  const Icon = iconMap[icon] || FiFileText;
  const isPositive = trend ? trend > 0 : null;

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center">
          <Icon className="text-primary-600 dark:text-primary-400" size={24} />
        </div>
        {trend !== null && trend !== undefined && (
          <div className={`flex items-center gap-1 text-sm font-medium ${
            isPositive ? 'text-green-600' : 'text-red-600'
          }`}>
            {isPositive ? <FiTrendingUp size={16} /> : <FiTrendingDown size={16} />}
            {Math.abs(trend)}%
          </div>
        )}
      </div>
      <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">{title}</p>
      <p className="text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
    </div>
  );
}
