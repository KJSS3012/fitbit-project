<script setup lang="ts">
import { sub, startOfDay, endOfDay, format, parseISO, isWithinInterval } from 'date-fns'
import type { Period } from '~/types/dashboard'
import MedicalNoteList from '~/components/shared/MedicalNoteList.vue'
import fitbitMockData from '~/assets/data/fitbit_api_mock_2025_2026.json'

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const route = useRoute()
const router = useRouter()
const { user, isDoctor } = useAuth()
const { fetchPatientMetrics, selectedPatientMetrics, isLoading } = useDoctorPatients()

const patientCpf = computed(() => route.params.cpf as string)

// Date range controls
const selectedPeriod = ref<Period>('week')
const customRange = ref({
  start: sub(new Date(), { days: 7 }),
  end: new Date()
})
const showCustomDialog = ref(false)
const customStartDate = ref('')
const customEndDate = ref('')
const toast = useToast()
const isNoteModalOpen = ref(false)

// Patient data from backend (not mock anymore)
const mockPatientData = ref({
  patient_name: '',
  patient_cpf: patientCpf.value,
  last_sync: '',
  is_data_outdated: false,
  metrics: [] as any[]
})

// Function to get mock data for a date range
const getMockDataForRange = (startDate: Date, endDate: Date) => {
  const start = startOfDay(startDate)
  const end = endOfDay(endDate)

  const metrics: any[] = []

  // Get steps data
  const stepsData = fitbitMockData['activities-steps'] || []
  const caloriesData = fitbitMockData['activities-calories'] || []
  const heartData = fitbitMockData['activities-heart'] || []
  const sleepData = fitbitMockData['sleep'] || []

  // Create a map of dates to aggregate data
  const dateMap = new Map<string, any>()

  // Process steps
  stepsData.forEach((item: any) => {
    const date = parseISO(item.dateTime)
    if (isWithinInterval(date, { start, end })) {
      const dateStr = format(date, 'yyyy-MM-dd')
      if (!dateMap.has(dateStr)) {
        dateMap.set(dateStr, {
          date: dateStr,
          steps: 0,
          calories: 0,
          hr_avg: 0,
          sleep_hours: 0
        })
      }
      dateMap.get(dateStr)!.steps = parseInt(item.value) || 0
    }
  })

  // Process calories
  caloriesData.forEach((item: any) => {
    const date = parseISO(item.dateTime)
    if (isWithinInterval(date, { start, end })) {
      const dateStr = format(date, 'yyyy-MM-dd')
      if (dateMap.has(dateStr)) {
        dateMap.get(dateStr)!.calories = parseInt(item.value) || 0
      }
    }
  })

  // Process heart rate
  heartData.forEach((item: any) => {
    const date = parseISO(item.dateTime)
    if (isWithinInterval(date, { start, end })) {
      const dateStr = format(date, 'yyyy-MM-dd')
      if (dateMap.has(dateStr)) {
        dateMap.get(dateStr)!.hr_avg = item.value?.restingHeartRate || 0
      }
    }
  })

  // Process sleep
  sleepData.forEach((item: any) => {
    const date = parseISO(item.dateOfSleep)
    if (isWithinInterval(date, { start, end })) {
      const dateStr = format(date, 'yyyy-MM-dd')
      if (dateMap.has(dateStr)) {
        const summary = item.levels?.summary || {}
        const deep = summary.deep?.minutes || 0
        const light = summary.light?.minutes || 0
        const rem = summary.rem?.minutes || 0
        const totalSleepMinutes = deep + light + rem
        dateMap.get(dateStr)!.sleep_hours = Math.round((totalSleepMinutes / 60) * 10) / 10 // Convert to hours with 1 decimal
      }
    }
  })

  // Convert map to array and sort by date
  return Array.from(dateMap.values()).sort((a, b) => a.date.localeCompare(b.date))
}

const currentDateRange = computed(() => {
  const now = new Date()

  switch (selectedPeriod.value) {
    case 'day':
      return { start: now, end: now }
    case 'week':
      return { start: sub(now, { weeks: 1 }), end: now }
    case 'month':
      return { start: sub(now, { months: 1 }), end: now }
    case 'custom':
      return customRange.value
    default:
      return { start: sub(now, { weeks: 1 }), end: now }
  }
})

const range = computed(() => ({
  start: startOfDay(new Date(currentDateRange.value.start)),
  end: endOfDay(new Date(currentDateRange.value.end))
}))

// Fetch data on mount
onMounted(async () => {
  if (!isDoctor.value) {
    navigateTo('/dashboard')
    return
  }

  await loadPatientData()
})

const loadPatientData = async () => {
  isLoading.value = true

  try {
    const startDate = format(range.value.start, 'yyyy-MM-dd')
    const endDate = format(range.value.end, 'yyyy-MM-dd')

    // Fetch real patient data from backend
    const realData = await fetchPatientMetrics(patientCpf.value, startDate, endDate)

    // If backend doesn't return metrics, use mock data
    if (!realData?.metrics || realData.metrics.length === 0) {
      const mockMetrics = getMockDataForRange(range.value.start, range.value.end)
      realData.metrics = mockMetrics
    }

    mockPatientData.value = realData

    // Update the composable data
    selectedPatientMetrics.value = realData

  } catch (error: any) {
    console.error('Failed to load patient data:', error)

    // Show error toast with backend message if available
    const errorMessage = error?.data?.detail || error?.message || 'Erro ao carregar dados do paciente'
    toast.add({
      title: 'Erro ao carregar dados',
      description: errorMessage,
      color: 'error',
      icon: 'i-lucide-alert-circle'
    })
  } finally {
    isLoading.value = false
  }
}

/**
 * Validates custom date range before applying
 */
const validateCustomRange = (start: string, end: string): boolean => {
  if (!start || !end) {
    toast.add({
      title: 'Período inválido',
      description: 'Data inicial e final são obrigatórias para o período customizado.',
      color: 'error',
      icon: 'i-lucide-alert-circle'
    })
    return false
  }

  const startDt = new Date(start)
  const endDt = new Date(end)
  const today = new Date()
  today.setHours(23, 59, 59, 999)

  if (startDt > endDt) {
    toast.add({
      title: 'Período inválido',
      description: 'Período inválido. Verifique as datas informadas.',
      color: 'error',
      icon: 'i-lucide-alert-circle'
    })
    return false
  }

  if (endDt > today) {
    toast.add({
      title: 'Data inválida',
      description: 'A data final não pode ser posterior à data de hoje.',
      color: 'error',
      icon: 'i-lucide-alert-circle'
    })
    return false
  }

  const diffTime = Math.abs(endDt.getTime() - startDt.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays > 365) {
    toast.add({
      title: 'Período muito longo',
      description: 'O período customizado não pode exceder 365 dias.',
      color: 'error',
      icon: 'i-lucide-alert-circle'
    })
    return false
  }

  return true
}

/**
 * Opens custom date range modal
 */
const openCustomDialog = () => {
  if (customRange.value) {
    customStartDate.value = customRange.value.start.toISOString().split('T')[0]!
    customEndDate.value = customRange.value.end.toISOString().split('T')[0]!
  } else {
    // Pre-fill with last week by default
    const today = new Date()
    const lastWeek = new Date()
    lastWeek.setDate(today.getDate() - 7)
    customStartDate.value = lastWeek.toISOString().split('T')[0]!
    customEndDate.value = today.toISOString().split('T')[0]!
  }
  showCustomDialog.value = true
}

/**
 * Applies custom date range
 */
const applyCustomRange = () => {
  if (!validateCustomRange(customStartDate.value, customEndDate.value)) {
    return
  }

  customRange.value = {
    start: new Date(customStartDate.value),
    end: new Date(customEndDate.value)
  }

  selectedPeriod.value = 'custom'
  showCustomDialog.value = false
  loadPatientData()
}

/**
 * Cancels custom range selection
 */
const cancelCustomRange = () => {
  showCustomDialog.value = false
  if (selectedPeriod.value === 'custom' && !customStartDate.value) {
    selectedPeriod.value = 'week'
  }
  customStartDate.value = ''
  customEndDate.value = ''
}

// Watch period changes
watch(selectedPeriod, () => {
  loadPatientData()
})

// Transform metrics for charts
const stepsData = computed(() => {
  if (!selectedPatientMetrics.value?.metrics) return []

  return selectedPatientMetrics.value.metrics.map((m: any) => ({
    date: m.date,
    value: m.steps
  })).reverse()
})

const heartRateData = computed(() => {
  if (!selectedPatientMetrics.value?.metrics) return []

  return selectedPatientMetrics.value.metrics.map((m: any) => ({
    date: m.date,
    value: m.hr_avg
  })).reverse()
})

const sleepData = computed(() => {
  if (!selectedPatientMetrics.value?.metrics) return []

  return selectedPatientMetrics.value.metrics.map((m: any) => ({
    date: m.date,
    value: m.sleep_hours
  })).reverse()
})

const caloriesData = computed(() => {
  if (!selectedPatientMetrics.value?.metrics) return []

  return selectedPatientMetrics.value.metrics.map((m: any) => ({
    date: m.date,
    value: m.calories
  })).reverse()
})

// Calculate stats
const stats = computed(() => {
  const metrics = selectedPatientMetrics.value?.metrics || []

  if (metrics.length === 0) {
    return {
      steps: { total: 0, average: 0, max: 0 },
      heartRate: { average: 0, min: 0, max: 0 },
      sleep: { totalHours: 0, averageHours: '0' },
      calories: { total: 0, average: 0 }
    }
  }

  const steps = metrics.map((m: any) => m.steps)
  const hrs = metrics.map((m: any) => m.hr_avg).filter((h: number) => h > 0)
  const sleep = metrics.map((m: any) => m.sleep_hours)
  const cals = metrics.map((m: any) => m.calories)

  return {
    steps: {
      total: steps.reduce((sum: number, v: number) => sum + v, 0),
      average: Math.round(steps.reduce((sum: number, v: number) => sum + v, 0) / steps.length),
      max: Math.max(...steps)
    },
    heartRate: {
      average: hrs.length > 0 ? Math.round(hrs.reduce((sum: number, v: number) => sum + v, 0) / hrs.length) : 0,
      min: hrs.length > 0 ? Math.min(...hrs) : 0,
      max: hrs.length > 0 ? Math.max(...hrs) : 0
    },
    sleep: {
      totalHours: Math.round(sleep.reduce((sum: number, v: number) => sum + v, 0)),
      averageHours: sleep.length > 0
        ? (sleep.reduce((sum: number, v: number) => sum + v, 0) / sleep.length).toFixed(1)
        : '0'
    },
    calories: {
      total: cals.reduce((sum: number, v: number) => sum + v, 0),
      average: Math.round(cals.reduce((sum: number, v: number) => sum + v, 0) / cals.length)
    }
  }
})

const goBack = () => {
  router.push('/patients')
}

const isFormValid = computed(() => {
  return !!customStartDate.value && !!customEndDate.value
})
</script>

<template>
  <UDashboardPanel>
    <template #header>
      <UDashboardNavbar :title="selectedPatientMetrics?.patient_name || 'Métricas do Paciente'">
        <template #leading>
          <UButton icon="i-lucide-arrow-left" color="neutral" variant="ghost" @click="goBack">
            Voltar
          </UButton>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-6 space-y-6">
        <!-- Patient Info + Outdated Alert -->
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold">{{ selectedPatientMetrics?.patient_name }}</h1>
            <p class="text-muted mt-1">CPF: {{ patientCpf }}</p>
          </div>

          <!-- Outdated Data Warning -->
          <UBadge v-if="selectedPatientMetrics?.is_data_outdated" color="warning" variant="subtle" size="lg">
            <UIcon name="i-heroicons-exclamation-triangle" class="size-4 mr-1" />
            Dados desatualizados ({{ selectedPatientMetrics?.last_sync }})
          </UBadge>

          <UBadge v-else-if="selectedPatientMetrics?.last_sync" color="success" variant="subtle" size="lg">
            <UIcon name="i-heroicons-check-circle" class="size-4 mr-1" />
            Atualizado ({{ selectedPatientMetrics?.last_sync }})
          </UBadge>
        </div>

        <!-- Period Selector -->
        <div class="flex items-center gap-3 flex-wrap">
          <UButtonGroup>
            <UButton :color="selectedPeriod === 'day' ? 'primary' : 'neutral'"
              :variant="selectedPeriod === 'day' ? 'solid' : 'ghost'" @click="selectedPeriod = 'day'">
              Dia
            </UButton>
            <UButton :color="selectedPeriod === 'week' ? 'primary' : 'neutral'"
              :variant="selectedPeriod === 'week' ? 'solid' : 'ghost'" @click="selectedPeriod = 'week'">
              Semana
            </UButton>
            <UButton :color="selectedPeriod === 'month' ? 'primary' : 'neutral'"
              :variant="selectedPeriod === 'month' ? 'solid' : 'ghost'" @click="selectedPeriod = 'month'">
              Mês
            </UButton>
          </UButtonGroup>

          <UButton icon="i-lucide-calendar" size="sm" variant="outline"
            :color="selectedPeriod === 'custom' ? 'primary' : 'secondary'" @click="openCustomDialog">
            {{ selectedPeriod === 'custom' ? 'Personalizado ✓' : 'Personalizado' }}
          </UButton>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="space-y-4">
          <USkeleton class="h-32" />
          <USkeleton class="h-64" />
          <USkeleton class="h-64" />
        </div>

        <!-- Metrics Content -->
        <template v-else-if="selectedPatientMetrics">
          <!-- Stats Cards -->
          <div class="grid grid-cols-2 gap-4">
            <DashboardStatsCard title="Passos Totais" :value="stats.steps.total.toLocaleString()"
              :subtitle="`Média: ${stats.steps.average.toLocaleString()}`" icon="i-lucide-footprints" color="primary" />
            <DashboardStatsCard title="Calorias" :value="stats.calories.total.toLocaleString()"
              :subtitle="`Média: ${stats.calories.average}`" icon="i-lucide-flame" color="warning" />
            <DashboardStatsCard title="Freq. Cardíaca" :value="stats.heartRate.average" subtitle="bpm médio"
              icon="i-lucide-heart-pulse" color="error" />
            <DashboardStatsCard title="Sono Médio" :value="stats.sleep.averageHours" subtitle="horas"
              icon="i-lucide-moon" color="info" />
          </div>

          <!-- Charts -->
          <UCard>
            <template #header>
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold">Passos</h3>
                <UBadge color="neutral" variant="subtle">
                  {{ stepsData.length }} registros
                </UBadge>
              </div>
            </template>
            <DashboardBarChart :data="stepsData" label="Passos" color="#3b82f6" />
            <DashboardChartStats :data="stepsData" label="passos" />
          </UCard>

          <UCard>
            <template #header>
              <h3 class="text-lg font-semibold">Frequência Cardíaca em Repouso</h3>
            </template>
            <DashboardLineChart :data="heartRateData" label="BPM" color="#ef4444" />
            <DashboardChartStats :data="heartRateData" label="bpm" />
          </UCard>

          <UCard>
            <template #header>
              <h3 class="text-lg font-semibold">Sono</h3>
            </template>
            <DashboardLineChart :data="sleepData" label="Horas" color="#8b5cf6" />
            <DashboardChartStats :data="sleepData" label="horas" />
          </UCard>

          <UCard>
            <template #header>
              <h3 class="text-lg font-semibold">Calorias</h3>
            </template>
            <DashboardBarChart :data="caloriesData" label="Calorias" color="#f59e0b" />
            <DashboardChartStats :data="caloriesData" label="kcal" />
          </UCard>
        </template>

        <!-- No Data State -->
        <div v-else class="text-center py-12">
          <UIcon name="i-lucide-database-zap" class="size-16 text-muted mx-auto mb-4" />
          <h3 class="text-lg font-semibold mb-2">Nenhum dado disponível</h3>
          <p class="text-muted">
            Não há métricas para este paciente no período selecionado
          </p>
        </div>
      </div>
    </template>
  </UDashboardPanel>

  <MedicalNoteList :patient-cpf="patientCpf" />

  <!-- Custom Date Range Modal -->
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
              <UInput v-model="customStartDate" type="date" icon="i-lucide-calendar" />
            </div>

            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Data Final <span class="text-red-500">*</span>
              </label>
              <UInput v-model="customEndDate" type="date" icon="i-lucide-calendar" />
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

  <!-- Note Modal -->
</template>