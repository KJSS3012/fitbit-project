<script setup lang="ts">
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const { user, isPatient, isDoctor, isLoading } = useAuth()

// Wait for auth to load before redirecting
watchEffect(() => {
  if (isLoading.value) return

  if (isPatient.value) {
    navigateTo('/dashboard/main', { replace: true })
  } else if (isDoctor.value) {
    navigateTo('/patients', { replace: true })
  }
})
</script>

<template>
  <UDashboardPanel>
    <template #body>
      <div class="flex items-center justify-center min-h-screen">
        <div class="text-center">
          <UIcon name="i-lucide-loader-2" class="size-12 animate-spin text-primary mx-auto mb-4" />
          <p class="text-muted">Carregando...</p>
        </div>
      </div>
    </template>
  </UDashboardPanel>
</template>
