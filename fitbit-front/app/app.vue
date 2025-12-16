<script setup lang="ts">
useHead({
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1' }
  ],
  htmlAttrs: {
    lang: 'pt-BR'
  }
})

useSeoMeta({
  titleTemplate: '%s · Fitbit Project',
  description: 'Sistema de Monitoramento de Saúde'
})
</script>

<template>
  <ConfigProvider>
    <UApp>
      <NuxtPage />
    </UApp>
  </ConfigProvider>
</template>
