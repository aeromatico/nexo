<template>
  <div class="flex h-screen bg-slate-50">
    <!-- Sidebar -->
    <aside class="w-64 bg-white border-r border-slate-200">
      <div class="p-6">
        <h1 class="text-2xl font-bold text-primary-600">Nexo Admin</h1>
      </div>
      <nav class="px-4 py-6 space-y-2">
        <router-link
          to="/"
          class="block px-4 py-2 rounded-lg text-slate-700 hover:bg-slate-100"
        >
          Dashboard
        </router-link>
        <router-link
          to="/tenants"
          class="block px-4 py-2 rounded-lg text-slate-700 hover:bg-slate-100"
        >
          Tenants
        </router-link>
        <router-link
          to="/analytics"
          class="block px-4 py-2 rounded-lg text-slate-700 hover:bg-slate-100"
        >
          Analytics
        </router-link>
        <router-link
          to="/settings"
          class="block px-4 py-2 rounded-lg text-slate-700 hover:bg-slate-100"
        >
          Configuración
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-auto">
      <div class="max-w-7xl mx-auto">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
  font-family: 'Inter', system-ui, sans-serif;
  @apply bg-slate-50;
}
</style>
