<script setup lang="ts">
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const { user, isDoctor } = useAuth()
const router = useRouter()
const { authorizedPatients, isLoading, fetchAuthorizedPatients } = useDoctorPatients()

interface Patient {
  cpf: string
  name: string
}

const searchQuery = ref('')

const patients = computed(() => authorizedPatients.value.map(p => ({
  id: p.cpf,
  name: p.name,
  cpf: p.cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4'),
  status: 'active' as const
})))

const filteredPatients = computed(() => {
  if (!searchQuery.value) return patients.value

  const query = searchQuery.value.toLowerCase()
  return patients.value.filter(p =>
    p.name.toLowerCase().includes(query) ||
    p.cpf.includes(query)
  )
})

const getStatusColor = (status: string) => {
  return status === 'active' ? 'success' : 'neutral'
}

const viewPatientDashboard = (patientId: string) => {
  // Navigate to patient metrics page with CPF
  const patient = patients.value.find(p => p.id === patientId)
  if (patient) {
    router.push(`/patients/${patient.cpf.replace(/\D/g, '')}/metrics`)
  }
}

onMounted(async () => {
  if (!isDoctor.value) {
    navigateTo('/dashboard')
    return
  }

  try {
    await fetchAuthorizedPatients()
  } catch (error) {
    console.error('Failed to load patients:', error)
  }
})
</script>

<template>
  <UDashboardPanel>
    <template #header>
      <UDashboardNavbar title="Meus Pacientes">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-6 space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold">Pacientes</h1>
            <p class="text-muted mt-1">Gerencie e visualize os dados dos seus pacientes</p>
          </div>

          <UBadge color="primary" variant="subtle" size="lg">
            {{ filteredPatients.length }} paciente{{ filteredPatients.length !== 1 ? 's' : '' }}
          </UBadge>
        </div>

        <UInput v-model="searchQuery" icon="i-lucide-search" placeholder="Buscar por nome ou CPF..." size="lg" />

        <div v-if="isLoading" class="space-y-4">
          <USkeleton v-for="i in 3" :key="i" class="h-24" />
        </div>

        <div v-else-if="filteredPatients.length === 0" class="text-center py-12">
          <UIcon name="i-lucide-users" class="size-16 text-muted mx-auto mb-4" />
          <h3 class="text-lg font-semibold mb-2">Nenhum paciente encontrado</h3>
          <p class="text-muted">
            {{ searchQuery ? 'Tente ajustar sua busca' : 'Você ainda não tem pacientes cadastrados' }}
          </p>
        </div>

        <div v-else class="grid gap-4">
          <UCard v-for="patient in filteredPatients" :key="patient.id"
            class="hover:bg-elevated/50 transition-colors cursor-pointer" @click="viewPatientDashboard(patient.id)">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4">
                <UAvatar :alt="patient.name" size="lg">
                  {{ patient.name.charAt(0) }}
                </UAvatar>

                <div>
                  <div class="flex items-center gap-2">
                    <h3 class="font-semibold text-lg">{{ patient.name }}</h3>
                    <UBadge :color="getStatusColor(patient.status)" variant="subtle" size="xs">
                      {{ patient.status === 'active' ? 'Ativo' : 'Inativo' }}
                    </UBadge>
                  </div>
                  <div class="flex items-center gap-4 mt-1 text-sm text-muted">
                    <span class="flex items-center gap-1">
                      <UIcon name="i-lucide-fingerprint" class="size-4" />
                      {{ patient.cpf }}
                    </span>
                  </div>
                </div>
              </div>

              <UButton icon="i-lucide-arrow-right" color="neutral" variant="ghost" square />
            </div>
          </UCard>
        </div>
      </div>
    </template>
  </UDashboardPanel>
</template>
