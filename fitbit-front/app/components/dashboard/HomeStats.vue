<script setup lang="ts">
import type { Period, Range, Stat } from '~/types/dashboard'
import { randomInt } from '~/utils/dashboard'

const props = defineProps<{
  period: Period
  range: Range
}>()

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0
  })
}

const baseStats = [{
  title: 'Pacientes',
  icon: 'i-lucide-users',
  minValue: 50,
  maxValue: 200,
  minVariation: -15,
  maxVariation: 25
}, {
  title: 'Consultas',
  icon: 'i-lucide-calendar-check',
  minValue: 100,
  maxValue: 300,
  minVariation: -10,
  maxVariation: 20
}, {
  title: 'Taxa de Adesão',
  icon: 'i-lucide-activity',
  minValue: 65,
  maxValue: 95,
  minVariation: -5,
  maxVariation: 15,
  formatter: (value: number) => `${value}%`
}, {
  title: 'Dispositivos Conectados',
  icon: 'i-simple-icons-fitbit',
  minValue: 30,
  maxValue: 150,
  minVariation: -5,
  maxVariation: 15
}]

const { data: stats } = await useAsyncData<Stat[]>('stats', async () => {
  return baseStats.map((stat) => {
    const value = randomInt(stat.minValue, stat.maxValue)
    const variation = randomInt(stat.minVariation, stat.maxVariation)

    return {
      title: stat.title,
      icon: stat.icon,
      value: stat.formatter ? stat.formatter(value) : value,
      variation
    }
  })
}, {
  watch: [() => props.period, () => props.range],
  default: () => []
})
</script>

<template>
  <UPageGrid class="lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-px">
    <UPageCard v-for="(stat, index) in stats" :key="index" :icon="stat.icon" :title="stat.title"
      to="/dashboard/patients" variant="subtle" :ui="{
        container: 'gap-y-1.5',
        wrapper: 'items-start',
        leading: 'p-2.5 rounded-full bg-primary/10 ring ring-inset ring-primary/25 flex-col',
        title: 'font-normal text-muted text-xs uppercase'
      }" class="lg:rounded-none first:rounded-l-lg last:rounded-r-lg hover:z-1">
      <div class="flex items-center gap-2">
        <span class="text-2xl font-semibold text-highlighted">
          {{ stat.value }}
        </span>

        <UBadge :color="stat.variation > 0 ? 'success' : 'error'" variant="subtle" class="text-xs">
          {{ stat.variation > 0 ? '+' : '' }}{{ stat.variation }}%
        </UBadge>
      </div>
    </UPageCard>
  </UPageGrid>
</template>
