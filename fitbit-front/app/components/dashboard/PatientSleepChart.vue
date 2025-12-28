<script setup lang="ts">
import { eachDayOfInterval, eachWeekOfInterval, eachMonthOfInterval, format } from 'date-fns'
import { VisXYContainer, VisAxis, VisCrosshair, VisTooltip, VisArea } from '@unovis/vue'
import { useElementSize } from '@vueuse/core'
import type { Period, Range } from '~/types/dashboard'

const cardRef = useTemplateRef<HTMLElement | null>('cardRef')

const props = defineProps<{
  data: Array<{ date: string; value: number }>
  period: Period
  range: Range
}>()

type DataRecord = {
  date: Date
  hours: number
  minutes: number
}

const { width } = useElementSize(cardRef)

const chartData = computed<DataRecord[]>(() => {
  return props.data.map(item => ({
    date: new Date(item.date),
    hours: Math.floor(item.value / 60),
    minutes: item.value % 60
  }))
})

const x = (_: DataRecord, i: number) => i
const y = (d: DataRecord) => d.hours + (d.minutes / 60)

const totalMinutes = computed(() => props.data.reduce((acc, item) => acc + item.value, 0))
const averageMinutes = computed(() => Math.round(totalMinutes.value / props.data.length))
const averageHours = computed(() => Math.floor(averageMinutes.value / 60))
const averageMins = computed(() => averageMinutes.value % 60)

const formatDate = (date: Date): string => {
  return ({
    daily: format(date, 'd MMM'),
    weekly: format(date, 'd MMM'),
    monthly: format(date, 'MMM yyyy')
  })[props.period]
}

const xTicks = (i: number) => {
  if (i === 0 || i === chartData.value.length - 1 || !chartData.value[i]) {
    return ''
  }

  return formatDate(chartData.value[i].date)
}

const template = (d: DataRecord) => `${formatDate(d.date)}: ${d.hours}h ${d.minutes}m`
</script>

<template>
  <UCard ref="cardRef" :ui="{ root: 'overflow-visible', body: '!px-0 !pt-0 !pb-3' }">
    <template #header>
      <div class="flex items-center justify-between">
        <div>
          <p class="text-xs text-muted uppercase mb-1.5">
            Sono Total
          </p>
          <p class="text-3xl text-highlighted font-semibold">
            {{ Math.floor(totalMinutes / 60) }}h {{ totalMinutes % 60 }}m
          </p>
        </div>
        <div class="text-right">
          <p class="text-xs text-muted uppercase mb-1.5">
            Média por Noite
          </p>
          <p class="text-2xl text-highlighted font-semibold">
            {{ averageHours }}h {{ averageMins }}m
          </p>
        </div>
      </div>
    </template>

    <VisXYContainer :data="chartData" :padding="{ top: 40 }" class="h-96" :width="width">
      <VisArea :x="x" :y="y" color="rgb(59, 130, 246)" :opacity="0.6" />

      <VisAxis type="x" :x="x" :tick-format="xTicks" />

      <VisCrosshair color="rgb(59, 130, 246)" :template="template" />

      <VisTooltip />
    </VisXYContainer>
  </UCard>
</template>

<style scoped>
.unovis-xy-container {
  --vis-crosshair-line-stroke-color: rgb(59, 130, 246);
  --vis-crosshair-circle-stroke-color: var(--ui-bg);

  --vis-axis-grid-color: var(--ui-border);
  --vis-axis-tick-color: var(--ui-border);
  --vis-axis-tick-label-color: var(--ui-text-dimmed);

  --vis-tooltip-background-color: var(--ui-bg);
  --vis-tooltip-border-color: var(--ui-border);
  --vis-tooltip-text-color: var(--ui-text-highlighted);
}
</style>
