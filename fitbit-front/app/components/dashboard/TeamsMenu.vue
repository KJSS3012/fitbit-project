<script setup lang="ts">
import type { DropdownMenuItem } from '@nuxt/ui'

defineProps<{
  collapsed?: boolean
}>()

const { user, isDoctor } = useAuth()

// Apenas médicos veem o menu de unidades/clínicas
const teams = computed(() => {
  if (!isDoctor.value) {
    return [{
      label: 'Minha Conta',
      avatar: {
        src: `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.value?.id}`,
        alt: user.value?.name || 'Paciente'
      }
    }]
  }

  return [{
    label: 'Clínica Principal',
    avatar: {
      src: 'https://api.dicebear.com/7.x/shapes/svg?seed=clinic',
      alt: 'Clínica Principal'
    }
  }, {
    label: 'Unidade Norte',
    avatar: {
      src: 'https://api.dicebear.com/7.x/shapes/svg?seed=north',
      alt: 'Unidade Norte'
    }
  }, {
    label: 'Unidade Sul',
    avatar: {
      src: 'https://api.dicebear.com/7.x/shapes/svg?seed=south',
      alt: 'Unidade Sul'
    }
  }]
})

const selectedTeam = ref(teams.value[0])

const items = computed<DropdownMenuItem[][]>(() => {
  const menuItems: DropdownMenuItem[][] = [teams.value.map(team => ({
    ...team,
    onSelect() {
      selectedTeam.value = team
    }
  }))]

  // Apenas médicos podem criar/gerenciar unidades
  if (isDoctor.value) {
    menuItems.push([{
      label: 'Criar unidade',
      icon: 'i-lucide-circle-plus'
    } as DropdownMenuItem, {
      label: 'Gerenciar unidades',
      icon: 'i-lucide-cog'
    } as DropdownMenuItem])
  }

  return menuItems
})
</script>

<template>
  <UDropdownMenu :items="items" :content="{ align: 'center', collisionPadding: 12 }"
    :ui="{ content: collapsed ? 'w-40' : 'w-(--reka-dropdown-menu-trigger-width)' }">
    <UButton v-bind="{
      ...selectedTeam,
      label: collapsed ? undefined : selectedTeam?.label,
      trailingIcon: collapsed ? undefined : 'i-lucide-chevrons-up-down'
    }" color="neutral" variant="ghost" block :square="collapsed" class="data-[state=open]:bg-elevated"
      :class="[!collapsed && 'py-2']" :ui="{
        trailingIcon: 'text-dimmed'
      }" />
  </UDropdownMenu>
</template>
