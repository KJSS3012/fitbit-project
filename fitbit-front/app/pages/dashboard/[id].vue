<script setup lang="ts">
import { sub } from 'date-fns'
import type { Period, Range } from '~/types/dashboard'
import { useDashboard } from '~/composables/useDashboard'

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const route = useRoute()
const router = useRouter()
const { isNotificationsSlideoverOpen } = useDashboard()
const { user, isPatient, isDoctor } = useAuth()
const runtimeConfig = useRuntimeConfig()

const patientId = computed(() => route.params.id as string)

// Validação de acesso: paciente só pode ver seu próprio dashboard
if (isPatient.value && user.value && patientId.value !== user.value.id) {
  navigateTo(`/dashboard/${user.value.id}`)
}

// Verifica se é visualização do médico (apenas leitura)
const isDoctorView = computed(() => isDoctor.value && patientId.value !== user.value?.id)

// Verifica se pode editar configurações (apenas o próprio paciente)
const canEditSettings = computed(() => isPatient.value && patientId.value === user.value?.id)

const range = shallowRef<Range>({
  start: sub(new Date(), { days: 14 }),
  end: new Date()
})
const period = ref<Period>('daily')

interface PatientData {
  profile: {
    fullName: string
    avatar?: string
    email: string
  }
  steps: {
    today: number
    data: Array<{ date: string; value: number }>
  }
  heartRate: {
    resting: number
    data: Array<{ date: string; value: number }>
  }
  sleep: {
    totalMinutes: number
    data: Array<{ date: string; value: number }>
  }
  lastSync: string
}

const loading = ref(false)
const error = ref<string | null>(null)
const patientData = ref<PatientData | null>(null)

const loadPatientData = async () => {
  loading.value = true
  error.value = null

  try {
    // TODO: Substituir por chamada real à API
    // const data = await $fetch(`/api/patients/${patientId.value}/dashboard`, {
    //   baseURL: runtimeConfig.public.apiBase,
    //   credentials: 'include',
    //   query: {
    //     startDate: range.value.start.toISOString(),
    //     endDate: range.value.end.toISOString(),
    //     period: period.value
    //   }
    // })

    // Mock data para desenvolvimento
    await new Promise(resolve => setTimeout(resolve, 1000))

    patientData.value = {
      profile: {
        fullName: 'João Silva',
        email: 'joao@example.com',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=joao'
      },
      steps: {
        today: 8543,
        data: Array.from({ length: 14 }, (_, i) => ({
          date: sub(new Date(), { days: 13 - i }).toISOString(),
          value: Math.floor(Math.random() * 5000) + 5000
        }))
      },
      heartRate: {
        resting: 72,
        data: Array.from({ length: 14 }, (_, i) => ({
          date: sub(new Date(), { days: 13 - i }).toISOString(),
          value: Math.floor(Math.random() * 20) + 60
        }))
      },
      sleep: {
        totalMinutes: 432,
        data: Array.from({ length: 14 }, (_, i) => ({
          date: sub(new Date(), { days: 13 - i }).toISOString(),
          value: Math.floor(Math.random() * 180) + 300
        }))
      },
      lastSync: new Date().toISOString()
    }
  } catch (err: any) {
    error.value = err.message || 'Erro ao carregar dados do paciente'
  } finally {
    loading.value = false
  }
}

const hasInsufficientData = computed(() => {
  if (!patientData.value) return false
  const days = Math.ceil((range.value.end.getTime() - range.value.start.getTime()) / (1000 * 60 * 60 * 24))
  return period.value === 'monthly' && days < 28
})

watch([() => range.value, () => period.value], () => {
  loadPatientData()
})

onMounted(() => {
  loadPatientData()
})
</script>

<template>
  <UDashboardPanel id="patient-dashboard">
    <template #header>
      <UDashboardNavbar :title="patientData?.profile.fullName || 'Carregando...'" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UButton icon="i-lucide-arrow-left" color="neutral" variant="ghost" to="/dashboard" square />
        </template>

        <template #right>
          <UTooltip text="Notificações" :shortcuts="['N']">
            <UButton color="neutral" variant="ghost" square @click="isNotificationsSlideoverOpen = true">
              <UChip color="error" inset>
                <UIcon name="i-lucide-bell" class="size-5 shrink-0" />
              </UChip>
            </UButton>
          </UTooltip>

          <!-- Botão de configurações (apenas para o próprio paciente) -->
          <UButton v-if="canEditSettings" icon="i-lucide-settings" color="neutral" variant="ghost"
            to="/dashboard/settings">
            Configurações
          </UButton>

          <UButton icon="i-lucide-refresh-cw" color="neutral" variant="ghost" @click="loadPatientData"
            :loading="loading">
            Atualizar
          </UButton>
        </template>
      </UDashboardNavbar>

      <UDashboardToolbar>
        <template #left>
          <!-- Badge indicando modo visualização para médico -->
          <UBadge v-if="isDoctorView" color="info" variant="subtle" class="mr-4">
            <UIcon name="i-lucide-eye" class="size-4 mr-1" />
            Modo Visualização
          </UBadge>

          <DashboardHomeDateRangePicker v-model="range" class="-ms-1" />
          <DashboardHomePeriodSelect v-model="period" :range="range" />
        </template>

        <template #right>
          <div v-if="patientData" class="text-sm text-muted">
            Última sincronização: {{ new Date(patientData.lastSync).toLocaleString('pt-BR') }}
          </div>
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <!-- Loading State -->
      <div v-if="loading" class="space-y-6 p-6">
        <USkeleton class="h-32 w-full" />
        <USkeleton class="h-96 w-full" />
        <USkeleton class="h-96 w-full" />
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="p-6">
        <UCard>
          <div class="flex flex-col items-center gap-4 py-12">
            <UIcon name="i-lucide-alert-circle" class="size-16 text-error" />
            <div class="text-center">
              <h3 class="text-lg font-semibold mb-2">Erro ao carregar dados</h3>
              <p class="text-muted text-sm">{{ error }}</p>
            </div>
            <UButton @click="loadPatientData" icon="i-lucide-refresh-cw">
              Tentar novamente
            </UButton>
          </div>
        </UCard>
      </div>

      <!-- Empty State -->
      <div v-else-if="!patientData" class="p-6">
        <UCard>
          <div class="flex flex-col items-center gap-4 py-12">
            <UIcon name="i-lucide-database" class="size-16 text-muted" />
            <div class="text-center">
              <h3 class="text-lg font-semibold mb-2">Nenhum dado disponível</h3>
              <p class="text-muted text-sm">
                Este paciente ainda não sincronizou seus dados do Fitbit.
              </p>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Data Insufficient Warning -->
      <UAlert v-else-if="hasInsufficientData" color="warning" variant="subtle" icon="i-lucide-alert-triangle"
        title="Dados insuficientes para visualização Mensal"
        description="O período selecionado não contém dados suficientes para a visualização mensal. Por favor, selecione um período maior ou escolha a visualização diária ou semanal."
        class="mb-6" />

      <!-- Dashboard Content -->
      <div v-else class="space-y-6">
        <!-- Stats Cards -->
        <UPageGrid class="lg:grid-cols-3 gap-4 sm:gap-6">
          <UPageCard icon="i-lucide-footprints" title="Passos Hoje" variant="subtle" :ui="{
            container: 'gap-y-1.5',
            wrapper: 'items-start',
            leading: 'p-2.5 rounded-full bg-primary/10 ring ring-inset ring-primary/25 flex-col',
            title: 'font-normal text-muted text-xs uppercase'
          }">
            <span class="text-2xl font-semibold text-highlighted">
              {{ patientData.steps.today.toLocaleString('pt-BR') }}
            </span>
          </UPageCard>

          <UPageCard icon="i-lucide-heart-pulse" title="FC em Repouso" variant="subtle" :ui="{
            container: 'gap-y-1.5',
            wrapper: 'items-start',
            leading: 'p-2.5 rounded-full bg-error/10 ring ring-inset ring-error/25 flex-col',
            title: 'font-normal text-muted text-xs uppercase'
          }">
            <span class="text-2xl font-semibold text-highlighted">
              {{ patientData.heartRate.resting }} <span class="text-sm text-muted">bpm</span>
            </span>
          </UPageCard>

          <UPageCard icon="i-lucide-moon" title="Sono (última noite)" variant="subtle" :ui="{
            container: 'gap-y-1.5',
            wrapper: 'items-start',
            leading: 'p-2.5 rounded-full bg-info/10 ring ring-inset ring-info/25 flex-col',
            title: 'font-normal text-muted text-xs uppercase'
          }">
            <span class="text-2xl font-semibold text-highlighted">
              {{ Math.floor(patientData.sleep.totalMinutes / 60) }}h {{ patientData.sleep.totalMinutes % 60 }}m
            </span>
          </UPageCard>
        </UPageGrid>

        <!-- Charts -->
        <DashboardPatientStepsChart :data="patientData.steps.data" :period="period" :range="range" />
        <DashboardPatientHeartRateChart :data="patientData.heartRate.data" :period="period" :range="range" />
        <DashboardPatientSleepChart :data="patientData.sleep.data" :period="period" :range="range" />
      </div>
    </template>
  </UDashboardPanel>
</template>
