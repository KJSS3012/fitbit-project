<script setup lang="ts">
import { sub, startOfDay, endOfDay } from 'date-fns'
import type { Period, Range } from '~/types/dashboard'
import type { TimeFilter } from '~/composables/useFitbitData'
import { useDashboard } from '~/composables/useDashboard'

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const router = useRouter()
const { user, isPatient, isDoctor, fetchUser } = useAuth()
const { currentDateRange, isLoadingData, selectedPeriod } = useDashboard()
const {
  isSimulationMode,
  toggleSimulation,
  getStepsData,
  getHeartRateData,
  getSleepData,
  getCaloriesData,
  getStats,
  hasInsufficientData,
  fetchFitbitData
} = useFitbitData()

const {
  isFitbitConnected,
  isConnecting,
  connectFitbit,
  checkFitbitStatus,
  disconnectFitbit
} = useFitbitAuth()

// Fetch user data on mount
onMounted(async () => {
  await fetchUser()
  await checkFitbitStatus()

  // Force refresh data after Fitbit connection
  if (isFitbitConnected.value && !isSimulationMode.value) {
    await fetchFitbitData()
  }
})

// Security: No ID in URL - using authenticated user from JWT token
// Patient sees their own data, doctor redirects to /patients list

const isDoctorView = computed(() => false) // Doctors view patients list, not individual dashboard

const canEditSettings = computed(() => isPatient.value)

const range = computed<Range>(() => ({
  start: startOfDay(new Date(currentDateRange.value.start)),
  end: endOfDay(new Date(currentDateRange.value.end))
}))

/**
 * Maps filter period to TimeFilter format used by chart components
 */
const period = computed<TimeFilter>(() => {
  if (selectedPeriod.value === 'day') return 'daily'
  if (selectedPeriod.value === 'week') return 'weekly'
  if (selectedPeriod.value === 'month') return 'monthly'
  return 'daily' // custom usa daily como fallback
})

const handleExport = () => {
  router.push('/dashboard/export')
}

// Reactive data loaded asynchronously
const stepsData = ref<Array<{ date: string; value: number }>>([])
const heartRateData = ref<Array<{ date: string; value: number }>>([])
const sleepData = ref<Array<{ date: string; value: number }>>([])
const caloriesData = ref<Array<{ date: string; value: number }>>([])
const stats = ref({
  steps: { total: 0, average: 0, max: 0 },
  heartRate: { average: 0, min: 0, max: 0 },
  sleep: { totalHours: 0, averageHours: 0 as string | number },
  calories: { total: 0, average: 0 }
})

// Load data when dependencies change
watchEffect(async () => {
  const start = range.value.start
  const end = range.value.end
  const p = period.value

  stepsData.value = await getStepsData(start, end, p)
  heartRateData.value = await getHeartRateData(start, end, p)
  sleepData.value = await getSleepData(start, end, p)
  caloriesData.value = await getCaloriesData(start, end, p)
  stats.value = await getStats(start, end)
})

const hasData = computed(() =>
  isFitbitConnected.value || isSimulationMode.value
)

const showInsufficientDataWarning = computed(() =>
  isSimulationMode.value && hasInsufficientData(range.value.start, range.value.end, period.value)
)
</script>

<template>
  <UDashboardPanel id="patient-dashboard">
    <template #header>
      <UDashboardNavbar>
        <template #title>
          <span class="text-xl font-semibold">
            Olá, {{ user?.name || 'Usuário' }}!
          </span>
        </template>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <div class="flex items-center gap-2">
            <UBadge v-if="isFitbitConnected" color="primary" variant="subtle">
              <UIcon name="i-simple-icons-fitbit" class="size-4 mr-1" />
              Fitbit Conectado
            </UBadge>

            <UBadge v-if="isSimulationMode" color="success" variant="subtle">
              <UIcon name="i-lucide-flask-conical" class="size-4 mr-1" />
              Modo Simulação
            </UBadge>
          </div>

          <UPopover>
            <UButton icon="i-lucide-plus" color="primary" variant="soft" square />

            <template #content>
              <div class="p-2 w-64">
                <UButton v-if="!isFitbitConnected" label="Conectar Fitbit" icon="i-simple-icons-fitbit" color="primary"
                  variant="ghost" block class="justify-start mb-1" :loading="isConnecting" @click="connectFitbit" />
                <UButton v-else label="Desconectar Fitbit" icon="i-simple-icons-fitbit" color="error" variant="ghost"
                  block class="justify-start mb-1" @click="disconnectFitbit" />

                <UDivider class="my-1" />

                <UButton :label="isSimulationMode ? 'Desativar Simulação' : 'Simular Dados'"
                  :icon="isSimulationMode ? 'i-lucide-database-zap' : 'i-lucide-flask-conical'" color="neutral"
                  variant="ghost" block class="justify-start mb-1" @click="toggleSimulation" />
                <UButton label="Exportar Dados" icon="i-lucide-download" color="neutral" variant="ghost" block
                  class="justify-start" @click="handleExport" />
              </div>
            </template>
          </UPopover>

          <UButton v-if="canEditSettings" icon="i-lucide-settings" color="neutral" variant="ghost"
            to="/dashboard/settings" square />
        </template>
      </UDashboardNavbar>

      <UDashboardToolbar>
        <template #left>
          <div class="flex flex-col sm:flex-row items-start sm:items-center gap-3 w-full">
            <DashboardFilterBar />
          </div>
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <div v-if="isLoadingData" class="p-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
          <USkeleton v-for="i in 4" :key="i" class="h-32" />
        </div>
        <div class="space-y-6">
          <USkeleton v-for="i in 3" :key="i" class="h-96" />
        </div>
      </div>

      <div v-else-if="!hasData" class="p-6">
        <UCard>
          <div class="flex flex-col items-center gap-4 py-12">
            <UIcon name="i-lucide-database" class="size-16 text-muted" />
            <div class="text-center">
              <h3 class="text-lg font-semibold mb-2">Nenhum dado disponível</h3>
              <p class="text-muted text-sm mb-4">
                <template v-if="isSimulationMode">
                  Nenhum dado encontrado para o período selecionado.
                </template>
                <template v-else>
                  Ative o modo de simulação para visualizar dados de exemplo.
                </template>
              </p>
              <UButton v-if="!isSimulationMode" @click="toggleSimulation" icon="i-lucide-flask-conical" color="primary">
                Simular Dados
              </UButton>
            </div>
          </div>
        </UCard>
      </div>

      <div v-else class="space-y-6 p-6">
        <UAlert v-if="showInsufficientDataWarning" color="warning" variant="subtle" icon="i-lucide-alert-triangle"
          title="Dados insuficientes para visualização" class="mb-4">
          <template #description>
            <p v-if="period === 'monthly'">
              O período selecionado não contém dados suficientes para a visualização mensal.
              Por favor, selecione um período maior (mínimo 28 dias) ou escolha a visualização diária ou semanal.
            </p>
            <p v-else-if="period === 'weekly'">
              O período selecionado não contém dados suficientes para a visualização semanal.
              Por favor, selecione um período maior (mínimo 7 dias) ou escolha a visualização diária.
            </p>
          </template>
        </UAlert>

        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <DashboardStatsCard title="Passos Totais" :value="stats.steps.total.toLocaleString('pt-BR')" subtitle="passos"
            icon="i-lucide-footprints" color="primary" />
          <DashboardStatsCard title="Média de Passos" :value="stats.steps.average.toLocaleString('pt-BR')"
            subtitle="por dia" icon="i-lucide-trending-up" color="success" />
          <DashboardStatsCard title="FC Média" :value="stats.heartRate.average" subtitle="bpm"
            icon="i-lucide-heart-pulse" color="error" />
          <DashboardStatsCard title="Sono Médio" :value="stats.sleep.averageHours" subtitle="horas" icon="i-lucide-moon"
            color="info" />
        </div>

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
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold">Frequência Cardíaca em Repouso</h3>
              <UBadge color="neutral" variant="subtle">
                {{ heartRateData.length }} registros
              </UBadge>
            </div>
          </template>
          <DashboardLineChart :data="heartRateData" label="BPM" color="#ef4444" />
          <DashboardChartStats :data="heartRateData" label="bpm" />
        </UCard>

        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold">Sono (minutos)</h3>
              <UBadge color="neutral" variant="subtle">
                {{ sleepData.length }} registros
              </UBadge>
            </div>
          </template>
          <DashboardLineChart :data="sleepData" label="Minutos" color="#8b5cf6" :show-fill="true" />
          <DashboardChartStats :data="sleepData" label="minutos" />
        </UCard>

        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold">Calorias</h3>
              <UBadge color="neutral" variant="subtle">
                {{ caloriesData.length }} registros
              </UBadge>
            </div>
          </template>
          <DashboardLineChart :data="caloriesData" label="Calorias" color="#f59e0b" />
          <DashboardChartStats :data="caloriesData" label="kcal" />
        </UCard>
      </div>
    </template>
  </UDashboardPanel>
</template>
