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
  { label: 'Mês', value: 'month' }
])

// Computed to determine which tab should be active
const activeTabValue = computed(() => {
  return activePeriod.value
})

// Computed to check if custom date range is selected
const isCustomSelected = computed(() => !!customDateRange.value)

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

  activePeriod.value = next
  showCustomDialog.value = false
  changePeriod(next as any)
}

const applyCustomRange = async () => {
  if (setCustomDateRange(startDate.value, endDate.value)) {
    showCustomDialog.value = false
    activePeriod.value = 'custom'
    await changePeriod('custom' as any)
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
    <UTabs :model-value="activeTabValue" :items="periodTabs" @update:modelValue="onPeriodTabChange" />

    <UButton icon="i-lucide-calendar" size="sm" variant="outline"
      :color="isCustomSelected ? 'primary' : 'secondary'" @click="openFilterDialog">
      {{ isCustomSelected ? 'Personalizado ✓' : 'Personalizado' }}
    </UButton>

    <Teleport v-if="showCustomDialog" to="body">
      <Transition enter-active-class="transition-opacity duration-200" enter-from-class="opacity-0"
        enter-to-class="opacity-100" leave-active-class="transition-opacity duration-200" leave-from-class="opacity-100"
        leave-to-class="opacity-0">
        <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          @click.self="showCustomDialog = false">
          <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
            <h3 class="text-lg font-semibold mb-4">Período Personalizado</h3>

            <div class="space-y-4">
              <div class="space-y-2">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Data Inicial <span class="text-red-500">*</span>
                </label>
                <UInput v-model="startDate" type="date" icon="i-lucide-calendar" />
              </div>

              <div class="space-y-2">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Data Final <span class="text-red-500">*</span>
                </label>
                <UInput v-model="endDate" type="date" icon="i-lucide-calendar" />
              </div>

              <UAlert color="info" variant="subtle" icon="i-lucide-info" title="Importante">
                <template #description>
                  O período personalizado não pode exceder 1 ano e a data final não pode ser posterior à data de hoje.
                </template>
              </UAlert>
            </div>

            <div class="flex justify-end gap-2 mt-6">
              <UButton label="Cancelar" color="neutral" variant="ghost" @click="cancelCustomRange" />
              <UButton label="Aplicar Filtro" color="primary" :disabled="!isFormValid" @click="applyCustomRange" />
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>