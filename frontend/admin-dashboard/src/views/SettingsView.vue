<template>
  <div class="p-6 space-y-6">
    <h1 class="text-3xl font-bold text-slate-900">Configuración</h1>

    <div class="bg-white rounded-lg shadow p-6">
      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-slate-900 mb-2">
            Nombre de Instancia
          </label>
          <input
            type="text"
            class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            placeholder="Nexo"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-900 mb-2">
            Email de Soporte
          </label>
          <input
            type="email"
            class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            placeholder="soporte@nexo.bo"
          />
        </div>

        <button class="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700">
          Guardar Cambios
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
