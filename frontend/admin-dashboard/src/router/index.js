import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '@views/DashboardView.vue';
import TenantsView from '@views/TenantsView.vue';
import AnalyticsView from '@views/AnalyticsView.vue';
import SettingsView from '@views/SettingsView.vue';

const routes = [
  { path: '/', component: DashboardView, name: 'Dashboard' },
  { path: '/tenants', component: TenantsView, name: 'Tenants' },
  { path: '/analytics', component: AnalyticsView, name: 'Analytics' },
  { path: '/settings', component: SettingsView, name: 'Settings' }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
