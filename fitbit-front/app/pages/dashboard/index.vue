<script setup lang="ts">
import { useDashboard } from '~/composables/useDashboard'

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const { isNotificationsSlideoverOpen } = useDashboard()
const { user, isPatient, isDoctor } = useAuth()
const runtimeConfig = useRuntimeConfig()

// Se for paciente, redireciona para seu próprio dashboard
if (isPatient.value && user.value) {
  navigateTo(`/dashboard/${user.value.id}`)
}

interface Patient {
  id: string
  name: string
  email: string
  avatar?: string
  lastSync: string
  status: 'active' | 'inactive' | 'pending'
  stepsToday: number
  connectedAt: string
}

const loading = ref(false)
const patients = ref<Patient[]>([])

const loadPatients = async () => {
  // Apenas médicos podem ver a lista de pacientes
  if (!isDoctor.value) {
    return
  }

  loading.value = true
  try {
    // TODO: Substituir por chamada real à API
    // const data = await $fetch('/api/patients/authorized', {
    //   baseURL: runtimeConfig.public.apiBase,
    //   credentials: 'include'
    // })

    // Mock data para desenvolvimento
    await new Promise(resolve => setTimeout(resolve, 1000))
    patients.value = [
      {
        id: '1',
        name: 'João Silva',
        email: 'joao@example.com',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=joao',
        lastSync: new Date().toISOString(),
        status: 'active',
        stepsToday: 8543,
        connectedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7).toISOString()
      },
      {
        id: '2',
        name: 'Maria Santos',
        email: 'maria@example.com',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=maria',
        lastSync: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
        status: 'active',
        stepsToday: 12034,
        connectedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 14).toISOString()
      },
      {
        id: '3',
        name: 'Carlos Oliveira',
        email: 'carlos@example.com',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=carlos',
        lastSync: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
        status: 'inactive',
        stepsToday: 0,
        connectedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString()
      }
    ]
  } catch (error) {
    console.error('Erro ao carregar pacientes:', error)
  } finally {
    loading.value = false
  }
}

const statusConfig = {
  active: { label: 'Ativo', color: 'success' as const },
  inactive: { label: 'Inativo', color: 'error' as const },
  pending: { label: 'Pendente', color: 'neutral' as const }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('pt-BR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadPatients()
})
</script>

<template>
  <UDashboardPanel id="patients-list">
    <template #header>
      <UDashboardNavbar title="Meus Pacientes" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UTooltip text="Notificações" :shortcuts="['N']">
            <UButton color="neutral" variant="ghost" square @click="isNotificationsSlideoverOpen = true">
              <UChip color="error" inset>
                <UIcon name="i-lucide-bell" class="size-5 shrink-0" />
              </UChip>
            </UButton>
          </UTooltip>

          <UButton icon="i-lucide-refresh-cw" color="neutral" variant="ghost" @click="loadPatients" :loading="loading">
            Atualizar
          </UButton>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div v-if="loading" class="p-6">
        <div class="space-y-4">
          <USkeleton class="h-20 w-full" v-for="i in 3" :key="i" />
        </div>
      </div>

      <div v-else-if="patients.length === 0" class="p-6">
        <UCard>
          <div class="flex flex-col items-center gap-4 py-12">
            <UIcon name="i-lucide-users" class="size-16 text-muted" />
            <div class="text-center">
              <h3 class="text-lg font-semibold mb-2">Nenhum paciente encontrado</h3>
              <p class="text-muted text-sm">
                Você ainda não tem pacientes que autorizaram o compartilhamento de dados.
              </p>
            </div>
          </div>
        </UCard>
      </div>

      <div v-else class="divide-y divide-default">
        <NuxtLink v-for="patient in patients" :key="patient.id" :to="`/dashboard/${patient.id}`"
          class="block p-6 hover:bg-elevated/50 transition-colors">
          <div class="flex items-center gap-4">
            <UAvatar :src="patient.avatar" :alt="patient.name" size="lg" />

            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <h3 class="font-semibold text-highlighted truncate">{{ patient.name }}</h3>
                <UBadge :color="statusConfig[patient.status].color" variant="subtle" size="xs">
                  {{ statusConfig[patient.status].label }}
                </UBadge>
              </div>

              <p class="text-sm text-muted truncate">{{ patient.email }}</p>

              <div class="flex items-center gap-4 mt-2 text-xs text-dimmed">
                <span class="flex items-center gap-1">
                  <UIcon name="i-lucide-footprints" class="size-4" />
                  {{ patient.stepsToday.toLocaleString('pt-BR') }} passos hoje
                </span>
                <span class="flex items-center gap-1">
                  <UIcon name="i-lucide-clock" class="size-4" />
                  Última sinc: {{ formatDate(patient.lastSync) }}
                </span>
              </div>
            </div>

            <UIcon name="i-lucide-chevron-right" class="size-5 text-muted shrink-0" />
          </div>
        </NuxtLink>
      </div>
    </template>
  </UDashboardPanel>
</template>
