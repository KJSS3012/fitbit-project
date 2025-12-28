<script setup lang="ts">
import { sub } from 'date-fns'
import type { DropdownMenuItem } from '@nuxt/ui'
import type { Period, Range } from '~/types/dashboard'
import { useDashboard } from '~/composables/useDashboard'

definePageMeta({
  layout: 'dashboard'
})

const { isNotificationsSlideoverOpen } = useDashboard()

const items = [[{
  label: 'Novo paciente',
  icon: 'i-lucide-user-plus',
  to: '/patients/new'
}, {
  label: 'Nova consulta',
  icon: 'i-lucide-calendar-plus',
  to: '/dashboard/appointments/new'
}]] satisfies DropdownMenuItem[][]

const range = shallowRef<Range>({
  start: sub(new Date(), { days: 14 }),
  end: new Date()
})
const period = ref<Period>('daily')
</script>

<template>
  <UDashboardPanel id="home">
    <template #header>
      <UDashboardNavbar title="Dashboard" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UTooltip text="Notificações" :shortcuts="['N']">
            <UButton color="neutral" variant="ghost" square @click="isNotificationsSlideoverOpen = true">
              <UChip color="error" inset>
                <UIcon name="i-lucide-bell" class="size-5 shrink-0" />
              </UChip>
            </UButton>
          </UTooltip>

          <UDropdownMenu :items="items">
            <UButton icon="i-lucide-plus" size="md" class="rounded-full" />
          </UDropdownMenu>
        </template>
      </UDashboardNavbar>

      <UDashboardToolbar>
        <template #left>
          <!-- NOTE: The `-ms-1` class is used to align with the `DashboardSidebarCollapse` button here. -->
          <DashboardHomeDateRangePicker v-model="range" class="-ms-1" />

          <DashboardHomePeriodSelect v-model="period" :range="range" />
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <DashboardHomeStats :period="period" :range="range" />
      <DashboardHomeChart :period="period" :range="range" />
      <DashboardHomeActivities :period="period" :range="range" />
    </template>
  </UDashboardPanel>
</template>
