<script setup lang="ts">
import type { TabsItem } from '@nuxt/ui/runtime/components/Tabs.vue.js'

const { selectedPeriod, changePeriod, setCustomDateRange, customDateRange } = useDashboard()

type FilterPeriod = 'day' | 'week' | 'month' | 'custom'

const showCustomDialog = ref(true)
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
    label: customDateRange.value ? 'Personalizado ✓' : 'Personalizado',
    value: 'custom'
  }
])

/**
 * Opens the custom date range dialog and pre-fills with saved values if available
 */
const openFilterDialog = () => {
  if (customDateRange.value) {
    startDate.value = customDateRange.value.start
    endDate.value = customDateRange.value.end
  } else {
    // Pre-fill with last week by default
    const today = new Date()
    const lastWeek = new Date()
    lastWeek.setDate(today.getDate() - 7)
    startDate.value = lastWeek.toISOString().split('T')[0]!
    endDate.value = today.toISOString().split('T')[0]!
  }
  showCustomDialog.value = true
}

/**
 * Handles tab change. Opens modal if 'custom' is clicked.
 */
const onPeriodTabChange = (value: string | number) => {
  const next = value as FilterPeriod

  if (next === 'custom') {
    // Open modal instead of immediately switching
    openFilterDialog()
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
  // Reset to last non-custom period if custom was never saved
  if (!customDateRange.value) {
    activePeriod.value = lastNonCustomPeriod.value
  }
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

    <UModal v-model="showCustomDialog" title="Período Personalizado">
      <template #body>
        <div class="space-y-4">
          <div class="space-y-2">
            <label for="startDate" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Data Inicial <span class="text-red-500">*</span>
            </label>
            <UInput id="startDate" v-model="startDate" type="date" icon="i-lucide-calendar"
              placeholder="Selecione a data inicial" aria-label="Selecione a data inicial" />
          </div>

          <div class="space-y-2">
            <label for="endDate" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Data Final <span class="text-red-500">*</span>
            </label>
            <UInput id="endDate" v-model="endDate" type="date" icon="i-lucide-calendar"
              placeholder="Selecione a data final" aria-label="Selecione a data final" />
          </div>

          <UAlert color="info" variant="subtle" icon="i-lucide-info" title="Importante">
            <template #description>
              O período personalizado não pode exceder 1 ano e a data final não pode ser posterior à data de hoje.
            </template>
          </UAlert>
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
