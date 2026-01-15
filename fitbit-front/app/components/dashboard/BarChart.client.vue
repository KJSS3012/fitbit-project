<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  type ChartOptions
} from 'chart.js'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface Props {
  data: Array<{ date: string; value: number }>
  label: string
  color?: string
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  color: '#3b82f6',
  height: 300
})

const colorMode = useColorMode()

// Parse date string as local date to avoid timezone issues
const parseLocalDate = (dateStr: string): Date => {
  const [year, month, day] = dateStr.split('-').map(Number)
  return new Date(year, month - 1, day)
}

const chartData = computed(() => ({
  labels: props.data.map(item => {
    try {
      return format(parseLocalDate(item.date), 'dd/MM', { locale: ptBR })
    } catch {
      return item.date
    }
  }),
  datasets: [
    {
      label: props.label,
      data: props.data.map(item => item.value),
      backgroundColor: `${props.color}80`,
      borderColor: props.color,
      borderWidth: 2,
      borderRadius: 4,
      borderSkipped: false
    }
  ]
}))

const chartOptions = computed<ChartOptions<'bar'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: colorMode.value === 'dark' ? '#1f2937' : '#fff',
      titleColor: colorMode.value === 'dark' ? '#f9fafb' : '#111827',
      bodyColor: colorMode.value === 'dark' ? '#d1d5db' : '#4b5563',
      borderColor: colorMode.value === 'dark' ? '#374151' : '#e5e7eb',
      borderWidth: 1,
      padding: 12,
      displayColors: false,
      callbacks: {
        title: (context) => {
          const firstContext = context[0]
          if (!firstContext) return ''
          const index = firstContext.dataIndex
          if (index === undefined || !props.data[index]) return ''
          try {
            return format(new Date(props.data[index].date), 'dd MMM yyyy', { locale: ptBR })
          } catch {
            return props.data[index].date
          }
        }
      }
    }
  },
  scales: {
    x: {
      grid: {
        display: false
      },
      ticks: {
        color: colorMode.value === 'dark' ? '#9ca3af' : '#6b7280'
      }
    },
    y: {
      beginAtZero: true,
      grid: {
        color: colorMode.value === 'dark' ? '#374151' : '#f3f4f6'
      },
      ticks: {
        color: colorMode.value === 'dark' ? '#9ca3af' : '#6b7280'
      }
    }
  }
}))
</script>

<template>
  <div :style="{ height: `${height}px` }">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>
