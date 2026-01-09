<script setup lang="ts">
interface Props {
  data: Array<{ date: string; value: number }>
  label: string
}

const props = defineProps<Props>()

const stats = computed(() => {
  if (props.data.length === 0) {
    return {
      min: 0,
      max: 0,
      avg: 0,
      peak: 0
    }
  }

  const values = props.data.map(d => d.value)
  const sum = values.reduce((a, b) => a + b, 0)
  const avg = Math.round(sum / values.length)
  const min = Math.min(...values)
  const max = Math.max(...values)

  // Pico é o valor mais alto registrado
  const peakIndex = values.indexOf(max)

  return {
    min,
    max,
    avg,
    peak: max,
    peakDate: props.data[peakIndex]?.date
  }
})

const formatValue = (value: number) => {
  return value.toLocaleString('pt-BR')
}
</script>

<template>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 pt-4 border-t border-default">
    <div class="text-center">
      <p class="text-xs text-dimmed mb-1">Mínimo</p>
      <p class="text-lg font-semibold text-blue-600 dark:text-blue-400">
        {{ formatValue(stats.min) }}
      </p>
    </div>

    <div class="text-center">
      <p class="text-xs text-dimmed mb-1">Médio</p>
      <p class="text-lg font-semibold text-green-600 dark:text-green-400">
        {{ formatValue(stats.avg) }}
      </p>
    </div>

    <div class="text-center">
      <p class="text-xs text-dimmed mb-1">Máximo</p>
      <p class="text-lg font-semibold text-orange-600 dark:text-orange-400">
        {{ formatValue(stats.max) }}
      </p>
    </div>

    <div class="text-center">
      <p class="text-xs text-dimmed mb-1">Pico</p>
      <p class="text-lg font-semibold text-red-600 dark:text-red-400">
        {{ formatValue(stats.peak) }}
      </p>
    </div>
  </div>
</template>
