<script setup lang="ts">
import type { DropdownMenuItem } from '@nuxt/ui'

defineProps<{
  collapsed?: boolean
}>()

const teams = ref([{
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
}])
const selectedTeam = ref(teams.value[0])

const items = computed<DropdownMenuItem[][]>(() => {
  return [teams.value.map(team => ({
    ...team,
    onSelect() {
      selectedTeam.value = team
    }
  })), [{
    label: 'Criar unidade',
    icon: 'i-lucide-circle-plus'
  }, {
    label: 'Gerenciar unidades',
    icon: 'i-lucide-cog'
  }]]
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
