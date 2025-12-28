<script setup lang="ts">
import { eachDayOfInterval, eachWeekOfInterval, eachMonthOfInterval, format } from 'date-fns'
import { VisXYContainer, VisAxis, VisCrosshair, VisTooltip } from '@unovis/vue'
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
  value: number
}

const { width } = useElementSize(cardRef)

const chartData = computed<DataRecord[]>(() => {
  return props.data.map(item => ({
    date: new Date(item.date),
    value: item.value
  }))
})

const x = (_: DataRecord, i: number) => i
const y = (d: DataRecord) => d.value

const total = computed(() => chartData.value.reduce((acc: number, { value }) => acc + value, 0))
const average = computed(() => Math.round(total.value / chartData.value.length))

const formatNumber = new Intl.NumberFormat('pt-BR').format

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

const template = (d: DataRecord) => `${formatDate(d.date)}: ${formatNumber(d.value)} passos`
</script>

<template>
  <UCard ref="cardRef" :ui="{ root: 'overflow-visible', body: '!px-0 !pt-0 !pb-3' }">
    <template #header>
      <div class="flex items-center justify-between">
        <div>
          <p class="text-xs text-muted uppercase mb-1.5">
            Passos
          </p>
          <p class="text-3xl text-highlighted font-semibold">
            {{ formatNumber(total) }}
          </p>
        </div>
        <div class="text-right">
          <p class="text-xs text-muted uppercase mb-1.5">
            Média
          </p>
          <p class="text-2xl text-highlighted font-semibold">
            {{ formatNumber(average) }}
          </p>
        </div>
      </div>
    </template>

    <VisXYContainer :data="chartData" :padding="{ top: 40 }" class="h-96" :width="width">
      <VisBar :x="x" :y="y" color="var(--ui-primary)" :rounded-corners="4" />

      <VisAxis type="x" :x="x" :tick-format="xTicks" />

      <VisCrosshair color="var(--ui-primary)" :template="template" />

      <VisTooltip />
    </VisXYContainer>
  </UCard>
</template>

<style scoped>
.unovis-xy-container {
  --vis-crosshair-line-stroke-color: var(--ui-primary);
  --vis-crosshair-circle-stroke-color: var(--ui-bg);

  --vis-axis-grid-color: var(--ui-border);
  --vis-axis-tick-color: var(--ui-border);
  --vis-axis-tick-label-color: var(--ui-text-dimmed);

  --vis-tooltip-background-color: var(--ui-bg);
  --vis-tooltip-border-color: var(--ui-border);
  --vis-tooltip-text-color: var(--ui-text-highlighted);
}
</style>
