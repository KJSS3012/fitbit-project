<script setup lang="ts">
import type { DropdownMenuItem } from '@nuxt/ui'

defineProps<{
  collapsed?: boolean
  disableDropdown?: boolean
}>()

const { user, isDoctor } = useAuth()

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
  <template v-if="disableDropdown">
    <div class="flex items-center gap-2 px-3 py-2 text-sm text-muted">
      <UIcon name="i-lucide-building" class="size-4" />
      <span v-if="!collapsed">{{ selectedTeam?.label }}</span>
    </div>
  </template>
  <template v-else>
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
</template>
