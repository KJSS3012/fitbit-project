<script setup lang="ts">
import { sub, startOfDay, endOfDay } from 'date-fns'
import type { Period, Range } from '~/types/dashboard'
import type { TimeFilter } from '~/composables/useFitbitData'
import type { TabsItem } from '@nuxt/ui/runtime/components/Tabs.vue.js'
import { useDashboard } from '~/composables/useDashboard'

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const route = useRoute()
const router = useRouter()
const { user, isPatient, isDoctor } = useAuth()
const {
  isSimulationMode,
  toggleSimulation,
  getStepsData,
  getHeartRateData,
  getSleepData,
  getCaloriesData,
  getStats,
  hasInsufficientData
} = useFitbitData()

const patientId = computed(() => route.params.id as string)

const isDoctorView = computed(() => isDoctor.value && patientId.value !== user.value?.id)

const canEditSettings = computed(() => isPatient.value && patientId.value === user.value?.id)

const range = shallowRef<Range>({
  start: startOfDay(sub(new Date(), { days: 6 })),
  end: endOfDay(new Date())
})
const period = ref<TimeFilter>('daily')

const periodTabs: TabsItem[] = [
  { label: 'Diário', value: 'daily' },
  { label: 'Semanal', value: 'weekly' },
  { label: 'Mensal', value: 'monthly' }
]

const handleExport = () => {
  router.push('/dashboard/export')
}

const stepsData = computed(() => getStepsData(range.value.start, range.value.end, period.value))
const heartRateData = computed(() => getHeartRateData(range.value.start, range.value.end, period.value))
const sleepData = computed(() => getSleepData(range.value.start, range.value.end, period.value))
const caloriesData = computed(() => getCaloriesData(range.value.start, range.value.end, period.value))

const stats = computed(() => getStats(range.value.start, range.value.end))

const loading = ref(false)
const hasData = computed(() =>
  isSimulationMode.value && (
    stepsData.value.length > 0 ||
    heartRateData.value.length > 0 ||
    sleepData.value.length > 0
  )
)

const showInsufficientDataWarning = computed(() =>
  isSimulationMode.value && hasInsufficientData(range.value.start, range.value.end, period.value)
)

onMounted(() => {
  if (isPatient.value && user.value && patientId.value !== user.value.id) {
    navigateTo(`/dashboard/${user.value.id}`)
  }
})
</script>

<template>
  <UDashboardPanel id="patient-dashboard">
    <template #header>
      <UDashboardNavbar :title="user?.name || 'Dashboard'" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UButton v-if="isDoctorView" icon="i-lucide-arrow-left" color="neutral" variant="ghost" to="/dashboard"
            square />
          <UDashboardSidebarCollapse v-else />
        </template>

        <template #right>
          <UBadge v-if="isSimulationMode" color="success" variant="subtle" class="mr-2">
            <UIcon name="i-lucide-flask-conical" class="size-4 mr-1" />
            Modo Simulação
          </UBadge>

          <UPopover>
            <UButton icon="i-lucide-plus" color="primary" variant="soft" square />

            <template #content>
              <div class="p-2 w-64">
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
          <div class="flex items-center gap-3 w-full">
            <UBadge v-if="isDoctorView" color="info" variant="subtle">
              <UIcon name="i-lucide-eye" class="size-4 mr-1" />
              Modo Visualização
            </UBadge>

            <DashboardHomeDateRangePicker v-model="range" />

            <UTabs v-model="period" :items="periodTabs" />
          </div>
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <div v-if="!hasData" class="p-6">
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