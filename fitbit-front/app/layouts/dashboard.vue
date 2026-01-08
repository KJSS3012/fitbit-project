<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const route = useRoute()
const { user, isDoctor, isPatient } = useAuth()

const open = ref(false)

// Links dinâmicos baseados no tipo de usuário
const links = computed(() => {
  if (isDoctor.value) {
    return [[{
      label: 'Pacientes',
      icon: 'i-lucide-users',
      to: '/dashboard',
      onSelect: () => {
        open.value = false
      }
    }]] satisfies NavigationMenuItem[][]
  } else if (isPatient.value) {
    return [[{
      label: 'Meu Dashboard',
      icon: 'i-lucide-house',
      to: `/dashboard/${user.value?.id}`,
      onSelect: () => {
        open.value = false
      }
    }, {
      label: 'Configurações',
      icon: 'i-lucide-settings',
      to: '/dashboard/settings',
      onSelect: () => {
        open.value = false
      }
    }]] satisfies NavigationMenuItem[][]
  }

  return [[]] satisfies NavigationMenuItem[][]
})

const groups = computed(() => [{
  id: 'links',
  label: 'Ir para',
  items: links.value.flat()
}])
</script>

<template>
  <UDashboardGroup unit="rem">
    <UDashboardSidebar id="default" v-model:open="open" collapsible resizable class="bg-elevated/25"
      :ui="{ footer: 'lg:border-t lg:border-default' }">
      <template #header="{ collapsed }">
        <DashboardTeamsMenu :collapsed="collapsed" />
      </template>

      <template #default="{ collapsed }">
        <UDashboardSearchButton :collapsed="collapsed" class="bg-transparent ring-default" />

        <UNavigationMenu :collapsed="collapsed" :items="links[0]" orientation="vertical" tooltip popover />
      </template>

      <template #footer="{ collapsed }">
        <DashboardUserMenu :collapsed="collapsed" />
      </template>
    </UDashboardSidebar>

    <UDashboardSearch :groups="groups" />

    <slot />

    <DashboardNotificationsSlideover />
  </UDashboardGroup>
</template>
