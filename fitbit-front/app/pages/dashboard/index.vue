<script setup lang="ts">
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const { user, isPatient, isDoctor } = useAuth()

onMounted(() => {
  if (isPatient.value && user.value) {
    navigateTo(`/dashboard/${user.value.id}`)
  } else if (isDoctor.value) {
    navigateTo('/patients')
  }
})
</script>

<template>
  <UDashboardPanel>
    <template #body>
      <div class="flex items-center justify-center min-h-screen">
        <div class="text-center">
          <UIcon name="i-lucide-loader-2" class="size-12 animate-spin text-primary mx-auto mb-4" />
          <p class="text-muted">Redirecionando...</p>
        </div>
      </div>
    </template>
  </UDashboardPanel>
</template>
