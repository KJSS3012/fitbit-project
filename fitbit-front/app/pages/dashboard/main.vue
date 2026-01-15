<script setup lang="ts">
import { sub, startOfDay, endOfDay } from 'date-fns'
import type { Period, Range } from '~/types/dashboard'
import type { TimeFilter } from '~/composables/useFitbitData'
import { useDashboard } from '~/composables/useDashboard'
import FitbitConnect from '~/components/shared/FitbitConnect.vue'
import FilterBar from '~/components/dashboard/FilterBar.vue'
import MedicalNoteList from '~/components/shared/MedicalNoteList.vue'

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const router = useRouter()
const { user, isPatient, isDoctor, fetchUser } = useAuth()
const { currentDateRange, isLoadingData, selectedPeriod, customDateRange } = useDashboard()
const {
  isSimulationMode,
  isFitbitMode,
  lastSyncTime,
  enableFitbitMode,
  enableSimulationMode,
  syncFitbitData,
  toggleSimulation,
  getStepsData,
  getHeartRateData,
  getSleepData,
  getCaloriesData,
  getStats,
  hasInsufficientData,
  fetchFitbitData,
  checkSleepDataFreshness
} = useFitbitData()

const {
  isFitbitConnected,
  isConnecting,
  connectFitbit,
  checkFitbitStatus,
  disconnectFitbit
} = useFitbitAuth()

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

// Format last sync time (e.g., "há 2 minutos")
const formatLastSync = (syncTime: Date) => {
  const now = new Date()
  const diffMs = now.getTime() - syncTime.getTime()
  const diffMinutes = Math.floor(diffMs / 60000)

  if (diffMinutes < 1) return 'agora mesmo'
  if (diffMinutes === 1) return 'há 1 minuto'
  if (diffMinutes < 60) return `há ${diffMinutes} minutos`

  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours === 1) return 'há 1 hora'
  if (diffHours < 24) return `há ${diffHours} horas`

  return syncTime.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
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

const isRefreshing = ref(false)
const isSyncing = ref(false)

// Manual data refresh function
const refreshData = async () => {
  if (isRefreshing.value) return

  isRefreshing.value = true
  try {
    const start = range.value.start
    const end = range.value.end
    const p = period.value

    // Load all data in parallel
    const [steps, heartRate, sleep, calories, statistics] = await Promise.all([
      getStepsData(start, end, p),
      getHeartRateData(start, end, p),
      getSleepData(start, end, p),
      getCaloriesData(start, end, p),
      getStats(start, end, p)
    ])

    stepsData.value = steps
    heartRateData.value = heartRate
    sleepData.value = sleep
    caloriesData.value = calories
    stats.value = statistics
  } finally {
    isRefreshing.value = false
  }
}

// Manual Fitbit sync function
const handleSyncNow = async () => {
  if (isSyncing.value) return

  isSyncing.value = true
  try {
    // Calculate date range length
    const start = new Date(currentDateRange.value.start)
    const end = new Date(currentDateRange.value.end)
    const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1
    
    // Map range length to period parameter
    const periodParam = diffDays >= 30 ? '30d' : '7d'
    
    await syncFitbitData(periodParam)
    // Refresh UI after successful sync
    await refreshData()
  } catch (error) {
    // Error already handled by syncFitbitData with toast
    console.error('Sync failed:', error)
  } finally {
    isSyncing.value = false
  }
}

// Load data on mount only
onMounted(async () => {
  await fetchUser()
  await checkFitbitStatus()
  
  // Ensure reactive state is settled before loading data
  await nextTick()
  
  await refreshData()

  // Check for stale sleep data on mount
  if (isFitbitConnected.value) {
    await checkSleepDataFreshness('7d')
  }
})

// Refresh when period or mode changes
watch([selectedPeriod, isFitbitMode, isSimulationMode, customDateRange], () => {
  refreshData()
})

// Clear data when user changes (e.g., logout then login as different user)
watch(() => user.value?.cpf, (newCpf, oldCpf) => {
  if (newCpf && oldCpf && newCpf !== oldCpf) {
    // User has changed - clear all cached data
    stepsData.value = []
    heartRateData.value = []
    sleepData.value = []
    caloriesData.value = []
    stats.value = {
      steps: { total: 0, average: 0, max: 0 },
      heartRate: { average: 0, min: 0, max: 0 },
      sleep: { totalHours: 0, averageHours: '0' },
      calories: { total: 0, average: 0 }
    }
  }
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
      <UDashboardNavbar title="Meu Dashboard">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <div class="flex items-center gap-2">
            <!-- Sync Now Button (Fitbit only) -->
            <UButton v-if="isFitbitMode && isFitbitConnected" icon="i-lucide-download-cloud" color="primary"
              variant="soft" size="sm" :loading="isSyncing" @click="handleSyncNow">
              Sincronizar Agora
            </UButton>

            <!-- Last Sync Time -->
            <div v-if="lastSyncTime" class="text-xs text-gray-500 dark:text-gray-400">
              Última atualização: {{ formatLastSync(lastSyncTime) }}
            </div>

            <!-- Refresh Button -->
            <UButton icon="i-lucide-refresh-cw" color="neutral" variant="ghost" size="sm" square :loading="isRefreshing"
              @click="refreshData" aria-label="Atualizar dados" />

            <UBadge v-if="isFitbitMode && isFitbitConnected" color="primary" variant="subtle">
              <UIcon name="i-simple-icons-fitbit" class="size-4 mr-1" />
              Fitbit Ativo
            </UBadge>

            <UBadge v-if="isSimulationMode" color="success" variant="subtle">
              <UIcon name="i-lucide-flask-conical" class="size-4 mr-1" />
              Simulação Ativa
            </UBadge>
          </div>

          <UPopover>
            <UButton icon="i-lucide-sliders-horizontal" color="neutral" variant="soft" square />

            <template #content>
              <div class="p-3 w-72">
                <div class="mb-3">
                  <p class="text-sm font-semibold mb-2">Fonte de Dados</p>
                  <div class="space-y-2">
                    <UButton :label="isFitbitMode ? 'Fitbit (Ativo)' : 'Ativar Fitbit'"
                      :icon="isFitbitMode ? 'i-lucide-check-circle' : 'i-simple-icons-fitbit'"
                      :color="isFitbitMode ? 'primary' : 'neutral'" :variant="isFitbitMode ? 'soft' : 'ghost'" block
                      class="justify-start" :disabled="false" @click="enableFitbitMode" />
                    <UButton :label="isSimulationMode ? 'Simulação (Ativa)' : 'Ativar Simulação'"
                      :icon="isSimulationMode ? 'i-lucide-check-circle' : 'i-lucide-flask-conical'"
                      :color="isSimulationMode ? 'success' : 'neutral'" :variant="isSimulationMode ? 'soft' : 'ghost'"
                      block class="justify-start" @click="enableSimulationMode" />
                  </div>
                </div>

                <div class="my-2 border-t border-gray-200 dark:border-gray-800" />

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
            <FilterBar />
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

  <!-- Patient Notes - Read Only -->
  <MedicalNoteList v-if="user" :patient-cpf="user.id" :read-only="true" />
</template>
