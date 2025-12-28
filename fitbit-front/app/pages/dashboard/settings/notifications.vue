<script setup lang="ts">
const state = reactive<{ [key: string]: boolean }>({
  email: true,
  desktop: false,
  health_alerts: true,
  daily_summary: false,
  doctor_access: true
})

const sections = [{
  title: 'Canais de Notificação',
  description: 'Como você deseja receber notificações?',
  fields: [{
    name: 'email',
    label: 'Email',
    description: 'Receber notificações por email.'
  }, {
    name: 'desktop',
    label: 'Desktop',
    description: 'Receber notificações no navegador.'
  }]
}, {
  title: 'Atualizações de Saúde',
  description: 'Notificações sobre seus dados de saúde.',
  fields: [{
    name: 'daily_summary',
    label: 'Resumo Diário',
    description: 'Receber um resumo diário de suas métricas de saúde.'
  }, {
    name: 'health_alerts',
    label: 'Alertas de Saúde',
    description: 'Receber alertas quando métricas importantes saírem do padrão.'
  }, {
    name: 'doctor_access',
    label: 'Acesso do Médico',
    description: 'Notificar quando seu médico acessar seus dados.'
  }]
}]

const toast = useToast()

async function onChange() {
  // TODO: Salvar preferências de notificação
  // await $fetch('/api/notifications/preferences', {
  //   method: 'PUT',
  //   body: state
  // })

  toast.add({
    title: 'Preferências atualizadas',
    description: 'Suas preferências de notificação foram salvas.',
    icon: 'i-lucide-check',
    color: 'success'
  })

  console.log(state)
}
</script>

<template>
  <div v-for="(section, index) in sections" :key="index">
    <UPageCard :title="section.title" :description="section.description" variant="naked" class="mb-4" />

    <UPageCard variant="subtle" :ui="{ container: 'divide-y divide-default' }">
      <UFormField v-for="field in section.fields" :key="field.name" :name="field.name" :label="field.label"
        :description="field.description" class="flex items-center justify-between not-last:pb-4 gap-2">
        <USwitch v-model="state[field.name]" @update:model-value="onChange" />
      </UFormField>
    </UPageCard>
  </div>
</template>
