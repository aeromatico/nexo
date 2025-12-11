<template>
  <div class="p-6 space-y-6">
    <h1 class="text-3xl font-bold text-slate-900">Dashboard</h1>

    <!-- Stats Grid -->
    <div class="grid grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <p class="text-slate-600 text-sm">Total Tenants</p>
        <p class="text-3xl font-bold text-slate-900">0</p>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <p class="text-slate-600 text-sm">Usuarios Activos</p>
        <p class="text-3xl font-bold text-slate-900">0</p>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <p class="text-slate-600 text-sm">Facturas Hoy</p>
        <p class="text-3xl font-bold text-slate-900">0</p>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <p class="text-slate-600 text-sm">Revenue Mensual</p>
        <p class="text-3xl font-bold text-slate-900">Bs. 0</p>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-2 gap-6">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-bold mb-4">Crecimiento de Tenants</h2>
        <div style="height: 300px;" class="bg-slate-100 rounded flex items-center justify-center">
          <p class="text-slate-600">Gráfico</p>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-bold mb-4">Facturas por Día</h2>
        <div style="height: 300px;" class="bg-slate-100 rounded flex items-center justify-center">
          <p class="text-slate-600">Gráfico</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAdminStore } from '@store/admin';

const adminStore = useAdminStore();

onMounted(() => {
  adminStore.fetchAnalytics();
});
</script>
