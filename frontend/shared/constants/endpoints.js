export const ENDPOINTS = {
  // Auth
  LOGIN: '/frappe.auth.login',
  LOGOUT: '/frappe.auth.logout',
  GET_CURRENT_USER: '/frappe.client.get_value',

  // Dashboard
  GET_DASHBOARD_DATA: '/nexo_core.portal.customer_portal.get_dashboard_data',
  GET_STATISTICS: '/nexo_core.portal.customer_portal.get_statistics',

  // Invoices
  GET_INVOICES: '/nexo_core.portal.invoices.get_my_invoices',
  GET_INVOICE_DETAIL: '/nexo_core.portal.invoices.get_invoice_detail',
  DOWNLOAD_INVOICE_PDF: '/nexo_core.portal.invoices.download_invoice_pdf',
  VERIFY_INVOICE_QR: '/nexo_core.portal.invoices.verify_qr',

  // Orders
  GET_ORDERS: '/nexo_core.portal.orders.get_my_orders',
  GET_ORDER_DETAIL: '/nexo_core.portal.orders.get_order_detail',
  CREATE_ORDER: '/nexo_core.portal.orders.create_order',
  UPDATE_ORDER: '/nexo_core.portal.orders.update_order',

  // Payments
  GET_PAYMENT_METHODS: '/nexo_core.portal.payments.get_payment_methods',
  INITIATE_PAYMENT: '/nexo_core.portal.payments.initiate_payment',
  GET_PAYMENT_STATUS: '/nexo_core.portal.payments.get_payment_status',

  // Support
  GET_TICKETS: '/nexo_core.portal.support.get_my_tickets',
  GET_TICKET_DETAIL: '/nexo_core.portal.support.get_ticket_detail',
  CREATE_TICKET: '/nexo_core.portal.support.create_ticket',
  REPLY_TICKET: '/nexo_core.portal.support.reply_ticket',

  // Profile
  GET_PROFILE: '/nexo_core.portal.profile.get_profile',
  UPDATE_PROFILE: '/nexo_core.portal.profile.update_profile',
  CHANGE_PASSWORD: '/nexo_core.portal.profile.change_password',
  UPDATE_PREFERENCES: '/nexo_core.portal.profile.update_preferences',

  // E-commerce
  GET_PRODUCTS: '/nexo_core.ecommerce.products.get_products',
  GET_PRODUCT_DETAIL: '/nexo_core.ecommerce.products.get_product_detail',
  GET_CATEGORIES: '/nexo_core.ecommerce.categories.get_categories',
  PLACE_ORDER: '/nexo_core.ecommerce.orders.place_order',

  // Admin
  GET_TENANTS: '/nexo_core.admin.tenants.get_tenants',
  GET_TENANT_DETAIL: '/nexo_core.admin.tenants.get_tenant_detail',
  CREATE_TENANT: '/nexo_core.admin.tenants.create_tenant',
  SUSPEND_TENANT: '/nexo_core.admin.tenants.suspend_tenant',
  GET_ANALYTICS: '/nexo_core.admin.analytics.get_analytics',
};

export default ENDPOINTS;
