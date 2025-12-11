import axios from 'axios';
import { useAuthStore } from '@store/authStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/method';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const { token } = useAuthStore.getState();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response.data.message || response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      const { logout } = useAuthStore.getState();
      logout();
      window.location.href = '/login';
    }
    return Promise.reject(error.response?.data || error);
  }
);

// Auth endpoints
export const authAPI = {
  login: (email, password) =>
    apiClient.post('/frappe.client.get_list', {
      doctype: 'User',
      filters: [['email', '=', email]],
    }),
  logout: () =>
    apiClient.post('/frappe.client.logout'),
  getCurrentUser: () =>
    apiClient.get('/frappe.client.get', {
      params: { doctype: 'User', name: 'Administrator' },
    }),
};

// Dashboard endpoints
export const dashboardAPI = {
  getDashboardData: () =>
    apiClient.get('/nexo_core.portal.customer_portal.get_dashboard_data'),
  getStatistics: () =>
    apiClient.get('/nexo_core.portal.customer_portal.get_statistics'),
};

// Invoice endpoints
export const invoiceAPI = {
  getInvoices: (filters = {}) =>
    apiClient.get('/nexo_core.portal.invoices.get_my_invoices', {
      params: filters,
    }),
  getInvoiceDetail: (invoiceId) =>
    apiClient.get('/nexo_core.portal.invoices.get_invoice_detail', {
      params: { invoice_id: invoiceId },
    }),
  downloadInvoicePDF: (invoiceId) =>
    apiClient.get(`/nexo_core.portal.invoices.download_invoice_pdf`, {
      params: { invoice_id: invoiceId },
      responseType: 'blob',
    }),
  verifyInvoiceQR: (qrData) =>
    apiClient.post('/nexo_core.portal.invoices.verify_qr', {
      qr_data: qrData,
    }),
};

// Order endpoints
export const orderAPI = {
  getOrders: (filters = {}) =>
    apiClient.get('/nexo_core.portal.orders.get_my_orders', {
      params: filters,
    }),
  getOrderDetail: (orderId) =>
    apiClient.get('/nexo_core.portal.orders.get_order_detail', {
      params: { order_id: orderId },
    }),
  createOrder: (orderData) =>
    apiClient.post('/nexo_core.portal.orders.create_order', orderData),
  updateOrder: (orderId, updates) =>
    apiClient.post('/nexo_core.portal.orders.update_order', {
      order_id: orderId,
      ...updates,
    }),
};

// Payment endpoints
export const paymentAPI = {
  getPaymentMethods: () =>
    apiClient.get('/nexo_core.portal.payments.get_payment_methods'),
  initiatePayment: (paymentData) =>
    apiClient.post('/nexo_core.portal.payments.initiate_payment', paymentData),
  getPaymentStatus: (paymentId) =>
    apiClient.get('/nexo_core.portal.payments.get_payment_status', {
      params: { payment_id: paymentId },
    }),
};

// Support endpoints
export const supportAPI = {
  getTickets: (filters = {}) =>
    apiClient.get('/nexo_core.portal.support.get_my_tickets', {
      params: filters,
    }),
  getTicketDetail: (ticketId) =>
    apiClient.get('/nexo_core.portal.support.get_ticket_detail', {
      params: { ticket_id: ticketId },
    }),
  createTicket: (ticketData) =>
    apiClient.post('/nexo_core.portal.support.create_ticket', ticketData),
  replyToTicket: (ticketId, reply) =>
    apiClient.post('/nexo_core.portal.support.reply_ticket', {
      ticket_id: ticketId,
      reply: reply,
    }),
};

// Profile endpoints
export const profileAPI = {
  getProfile: () =>
    apiClient.get('/nexo_core.portal.profile.get_profile'),
  updateProfile: (profileData) =>
    apiClient.post('/nexo_core.portal.profile.update_profile', profileData),
  changePassword: (oldPassword, newPassword) =>
    apiClient.post('/nexo_core.portal.profile.change_password', {
      old_password: oldPassword,
      new_password: newPassword,
    }),
  updatePreferences: (preferences) =>
    apiClient.post('/nexo_core.portal.profile.update_preferences', preferences),
};

export default apiClient;
