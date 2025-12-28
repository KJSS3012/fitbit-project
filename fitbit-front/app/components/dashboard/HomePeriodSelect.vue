<script setup lang="ts">
import { eachDayOfInterval } from 'date-fns'
import type { Period, Range } from '~/types/dashboard'

const model = defineModel<Period>({ required: true })

const props = defineProps<{
  range: Range
}>()

const days = computed(() => eachDayOfInterval(props.range))

const periods = computed<Period[]>(() => {
  if (days.value.length <= 8) {
    return [
      'daily'
    ]
  }

  if (days.value.length <= 31) {
    return [
      'daily',
      'weekly'
    ]
  }

  return [
    'weekly',
    'monthly'
  ]
})

// Ensure the model value is always a valid period
watch(periods, () => {
  if (!periods.value.includes(model.value)) {
    model.value = periods.value[0]!
  }
})

const periodLabels = {
  daily: 'Diário',
  weekly: 'Semanal',
  monthly: 'Mensal'
}

const periodItems = computed(() => periods.value.map(p => ({
  label: periodLabels[p],
  value: p
})))
</script>

<template>
  <USelect v-model="model" :items="periodItems" variant="ghost" class="data-[state=open]:bg-elevated"
    :ui="{ trailingIcon: 'group-data-[state=open]:rotate-180 transition-transform duration-200' }" />
</template>
