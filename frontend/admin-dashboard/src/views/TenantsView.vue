<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-slate-900">Gestión de Tenants</h1>
      <button class="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700">
        Crear Tenant
      </button>
    </div>

    <!-- Tenants Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="border-b">
            <th class="px-6 py-4 text-left font-semibold">Nombre</th>
            <th class="px-6 py-4 text-left font-semibold">Subdomain</th>
            <th class="px-6 py-4 text-left font-semibold">Plan</th>
            <th class="px-6 py-4 text-left font-semibold">Estado</th>
            <th class="px-6 py-4 text-left font-semibold">Usuarios</th>
            <th class="px-6 py-4 text-left font-semibold">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr class="border-b hover:bg-slate-50" v-if="adminStore.tenants.length === 0">
            <td colspan="6" class="px-6 py-4 text-center text-slate-600">
              Sin tenants
            </td>
          </tr>
          <tr v-for="tenant in adminStore.tenants" :key="tenant.name" class="border-b hover:bg-slate-50">
            <td class="px-6 py-4">{{ tenant.tenant_name }}</td>
            <td class="px-6 py-4">{{ tenant.subdomain }}.nexo.bo</td>
            <td class="px-6 py-4">{{ tenant.plan }}</td>
            <td class="px-6 py-4">
              <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                {{ tenant.status }}
              </span>
            </td>
            <td class="px-6 py-4">{{ tenant.user_count }}</td>
            <td class="px-6 py-4 space-x-2">
              <button class="text-blue-600 hover:underline">Ver</button>
              <button class="text-red-600 hover:underline">Suspender</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAdminStore } from '@store/admin';

const adminStore = useAdminStore();

onMounted(() => {
  adminStore.fetchTenants();
});
</script>
