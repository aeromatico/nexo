import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_BASE_URL = 'http://localhost:8000/api/method';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const { token } = useAuthStore.getState();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response.data.message || response.data,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);

export const getDashboardData = () =>
  apiClient.get('/nexo_core.portal.customer_portal.get_dashboard_data');

export const getInvoices = () =>
  apiClient.get('/nexo_core.portal.invoices.get_my_invoices');

export const getOrders = () =>
  apiClient.get('/nexo_core.portal.orders.get_my_orders');

export const verifyInvoiceQR = (qrData: string) =>
  apiClient.post('/nexo_core.portal.invoices.verify_qr', { qr_data: qrData });
