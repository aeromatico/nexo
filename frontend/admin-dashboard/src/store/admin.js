import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAdminStore = defineStore('admin', () => {
  const tenants = ref([]);
  const analytics = ref({});
  const loading = ref(false);

  const fetchTenants = async () => {
    loading.value = true;
    try {
      // API call would go here
      tenants.value = [];
    } finally {
      loading.value = false;
    }
  };

  const fetchAnalytics = async () => {
    loading.value = true;
    try {
      // API call would go here
      analytics.value = {};
    } finally {
      loading.value = false;
    }
  };

  return { tenants, analytics, loading, fetchTenants, fetchAnalytics };
});
