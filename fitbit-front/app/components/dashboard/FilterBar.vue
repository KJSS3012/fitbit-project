<script setup lang="ts">
import type { TabsItem } from '@nuxt/ui/runtime/components/Tabs.vue.js'

const { selectedPeriod, changePeriod, setCustomDateRange, customDateRange } = useDashboard()

type FilterPeriod = 'day' | 'week' | 'month' | 'custom'

const showCustomDialog = ref(false)
const startDate = ref('')
const endDate = ref('')

const activePeriod = ref<FilterPeriod>(selectedPeriod.value)
const lastNonCustomPeriod = ref<FilterPeriod>(selectedPeriod.value === 'custom' ? 'week' : selectedPeriod.value)

watch(() => selectedPeriod.value, (value) => {
  activePeriod.value = value
  if (value !== 'custom') {
    lastNonCustomPeriod.value = value
  }
})

const periodTabs = computed<TabsItem[]>(() => [
  { label: 'Dia', value: 'day' },
  { label: 'Semana', value: 'week' },
  { label: 'Mês', value: 'month' },
  {
    label: 'Personalizado',
    value: 'custom',
    disabled: !customDateRange.value,
    badge: customDateRange.value ? '✓' : undefined
  }
])

/**
 * Opens the custom date range dialog and pre-fills with saved values if available
 */
const openFilterDialog = () => {
  if (customDateRange.value) {
    startDate.value = customDateRange.value.start
    endDate.value = customDateRange.value.end
  }
  showCustomDialog.value = true
}

/**
 * Handles tab change. Prevents selecting 'custom' tab without saved range.
 */
const onPeriodTabChange = (value: string | number) => {
  const next = value as FilterPeriod

  if (next === 'custom' && !customDateRange.value) {
    activePeriod.value = lastNonCustomPeriod.value
    return
  }

  activePeriod.value = next
  showCustomDialog.value = false
  changePeriod(next as any)
}

const applyCustomRange = () => {
  if (setCustomDateRange(startDate.value, endDate.value)) {
    showCustomDialog.value = false
    activePeriod.value = 'custom'
    changePeriod('custom' as any)
  }
}

const cancelCustomRange = () => {
  showCustomDialog.value = false
  startDate.value = ''
  endDate.value = ''
}

const isFormValid = computed(() => {
  return !!startDate.value && !!endDate.value
})
</script>

<template>
  <div class="flex items-center gap-3 flex-wrap">
    <UTabs :model-value="activePeriod" :items="periodTabs" @update:modelValue="onPeriodTabChange" />

    <UModal v-model="showCustomDialog" title="Período Customizado">
      <UButton icon="i-lucide-filter" color="neutral" variant="ghost" size="sm" square
        aria-label="Filtro personalizado" />

      <template #body>
        <div class="space-y-4">
          <UFormGroup label="Data Inicial" name="startDate" required>
            <UInput v-model="startDate" type="date" icon="i-lucide-calendar" placeholder="Selecione a data inicial"
              aria-label="Selecione a data inicial" />
          </UFormGroup>

          <UFormGroup label="Data Final" name="endDate" required>
            <UInput v-model="endDate" type="date" icon="i-lucide-calendar" placeholder="Selecione a data final"
              aria-label="Selecione a data final" />
          </UFormGroup>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton label="Cancelar" color="neutral" variant="ghost" @click="cancelCustomRange" />
          <UButton label="Aplicar Filtro" color="primary" :disabled="!isFormValid" @click="applyCustomRange" />
        </div>
      </template>
    </UModal>
  </div>
</template>
