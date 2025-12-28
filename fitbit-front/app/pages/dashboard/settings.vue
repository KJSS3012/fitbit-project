<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const { user, isPatient } = useAuth()

// Apenas pacientes podem acessar configurações
if (!isPatient.value) {
  navigateTo('/dashboard')
}

const links = [[{
  label: 'Geral',
  icon: 'i-lucide-user',
  to: '/dashboard/settings',
  exact: true
}, {
  label: 'Notificações',
  icon: 'i-lucide-bell',
  to: '/dashboard/settings/notifications'
}, {
  label: 'Segurança',
  icon: 'i-lucide-shield',
  to: '/dashboard/settings/security'
}, {
  label: 'Fitbit',
  icon: 'i-simple-icons-fitbit',
  to: '/dashboard/settings/fitbit'
}]] satisfies NavigationMenuItem[][]
</script>

<template>
  <UDashboardPanel id="settings" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar title="Configurações">
        <template #leading>
          <UButton icon="i-lucide-arrow-left" color="neutral" variant="ghost" :to="`/dashboard/${user?.id}`" square />
        </template>
      </UDashboardNavbar>

      <UDashboardToolbar>
        <UNavigationMenu :items="links" highlight class="-mx-1 flex-1" />
      </UDashboardToolbar>
    </template>

    <template #body>
      <div class="flex flex-col gap-4 sm:gap-6 lg:gap-12 w-full lg:max-w-2xl mx-auto">
        <NuxtPage />
      </div>
    </template>
  </UDashboardPanel>
</template>
