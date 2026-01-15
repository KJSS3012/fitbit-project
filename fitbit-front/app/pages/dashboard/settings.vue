<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const { user, isPatient, isDoctor } = useAuth()
const route = useRoute()

// Only redirect if not patient AND not doctor AND not already on settings page
if (!isPatient.value && !isDoctor.value && !route.path.startsWith('/dashboard/settings')) {
  navigateTo('/dashboard/main', { replace: true })
}

const links = [[{
  label: 'Geral',
  icon: 'i-lucide-user',
  to: '/dashboard/settings',
  exact: true
}, {
  label: 'Segurança',
  icon: 'i-lucide-shield',
  to: '/dashboard/settings/security'
}]] satisfies NavigationMenuItem[][]

// For doctors, only show Geral tab
const doctorLinks = [[{
  label: 'Geral',
  icon: 'i-lucide-user',
  to: '/dashboard/settings',
  exact: true
}]] satisfies NavigationMenuItem[][]

const navigationLinks = computed(() => {
  if (isDoctor.value) {
    return doctorLinks
  }
  return links
})
</script>

<template>
  <UDashboardPanel id="settings" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar title="Configurações">
        <template #leading>
          <UButton icon="i-lucide-arrow-left" color="neutral" variant="ghost" to="/dashboard/main" square />
        </template>
      </UDashboardNavbar>

      <UDashboardToolbar>
        <UNavigationMenu :items="navigationLinks" highlight class="-mx-1 flex-1" />
      </UDashboardToolbar>
    </template>

    <template #body>
      <div class="flex flex-col gap-4 sm:gap-6 lg:gap-12 w-full lg:max-w-2xl mx-auto">
        <NuxtPage />
      </div>
    </template>
  </UDashboardPanel>
</template>
