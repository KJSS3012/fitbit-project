<script setup lang="ts">
import { eachDayOfInterval, eachWeekOfInterval, eachMonthOfInterval, format } from 'date-fns'
import { VisXYContainer, VisLine, VisAxis, VisArea, VisCrosshair, VisTooltip } from '@unovis/vue'
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

const average = computed(() => {
  const sum = chartData.value.reduce((acc: number, { value }) => acc + value, 0)
  return Math.round(sum / chartData.value.length)
})

const min = computed(() => Math.min(...chartData.value.map(d => d.value)))
const max = computed(() => Math.max(...chartData.value.map(d => d.value)))

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

const template = (d: DataRecord) => `${formatDate(d.date)}: ${d.value} bpm`
</script>

<template>
  <UCard ref="cardRef" :ui="{ root: 'overflow-visible', body: '!px-0 !pt-0 !pb-3' }">
    <template #header>
      <div class="flex items-center justify-between">
        <div>
          <p class="text-xs text-muted uppercase mb-1.5">
            Frequência Cardíaca em Repouso
          </p>
          <p class="text-3xl text-highlighted font-semibold">
            {{ average }} <span class="text-lg text-muted">bpm</span>
          </p>
        </div>
        <div class="text-right">
          <p class="text-xs text-muted uppercase mb-1.5">
            Mín / Máx
          </p>
          <p class="text-xl text-highlighted font-semibold">
            {{ min }} / {{ max }} <span class="text-sm text-muted">bpm</span>
          </p>
        </div>
      </div>
    </template>

    <VisXYContainer :data="chartData" :padding="{ top: 40 }" class="h-96" :width="width">
      <VisLine :x="x" :y="y" color="rgb(239, 68, 68)" />
      <VisArea :x="x" :y="y" color="rgb(239, 68, 68)" :opacity="0.1" />

      <VisAxis type="x" :x="x" :tick-format="xTicks" />

      <VisCrosshair color="rgb(239, 68, 68)" :template="template" />

      <VisTooltip />
    </VisXYContainer>
  </UCard>
</template>

<style scoped>
.unovis-xy-container {
  --vis-crosshair-line-stroke-color: rgb(239, 68, 68);
  --vis-crosshair-circle-stroke-color: var(--ui-bg);

  --vis-axis-grid-color: var(--ui-border);
  --vis-axis-tick-color: var(--ui-border);
  --vis-axis-tick-label-color: var(--ui-text-dimmed);

  --vis-tooltip-background-color: var(--ui-bg);
  --vis-tooltip-border-color: var(--ui-border);
  --vis-tooltip-text-color: var(--ui-text-highlighted);
}
</style>
