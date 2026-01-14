<script setup lang="ts">
import { useAuthorization } from '~/composables/useAuthorization'
import { useAuth } from '~/composables/useAuth'

const toast = useToast()
const { user, token } = useAuth()

// Authorization (doctors)
const {
  authorizedDoctors,
  fetchAuthorizedDoctors,
  addDoctorAuthorization,
  toggleDoctorAuthorization,
  revokeAllAuthorizations,
  setDoctorDataType,
  isLoading: authLoading
} = useAuthorization()

const newDoctorCrm = ref('')
const isAddingDoctor = ref(false)

const handleAddDoctor = async () => {
  if (!token.value || !user.value) {
    toast.add({
      title: 'Erro de autenticação',
      description: 'Você precisa estar logado para adicionar médicos',
      color: 'error',
      icon: 'i-heroicons-x-circle'
    })
    return
  }
  if (!newDoctorCrm.value.trim()) return
  isAddingDoctor.value = true
  try {
    await addDoctorAuthorization(newDoctorCrm.value.trim())
    newDoctorCrm.value = ''
    // Refresh the list after adding
    await fetchAuthorizedDoctors()
  } catch (err) {
    // toast handled in composable
  } finally {
    isAddingDoctor.value = false
  }
}

const handleToggleDoctor = async (doctorCrm: string, doctorName: string) => {
  if (!token.value || !user.value) {
    toast.add({
      title: 'Erro de autenticação',
      description: 'Você precisa estar logado para alterar autorizações',
      color: 'error',
      icon: 'i-heroicons-x-circle'
    })
    return
  }
  try {
    await toggleDoctorAuthorization(doctorCrm, doctorName)
    // Refresh the list after toggling
    await fetchAuthorizedDoctors()
  } catch (err) {
    // toast handled in composable
  }
}

const handleSetDataType = async (crm: string, type: string) => {
  if (!token.value || !user.value) {
    toast.add({
      title: 'Erro de autenticação',
      description: 'Você precisa estar logado para alterar tipo de dados',
      color: 'error',
      icon: 'i-heroicons-x-circle'
    })
    return
  }
  try {
    await setDoctorDataType(crm, type)
    // Refresh the list after updating
    await fetchAuthorizedDoctors()
  } catch (err) {
    // toast handled in composable
  }
}

const handleRevokeAll = async () => {
  if (!token.value || !user.value) {
    toast.add({
      title: 'Erro de autenticação',
      description: 'Você precisa estar logado para revogar autorizações',
      color: 'error',
      icon: 'i-heroicons-x-circle'
    })
    return
  }
  try {
    await revokeAllAuthorizations()
    // Refresh the list after revoking all
    await fetchAuthorizedDoctors()
  } catch (err) {
    // toast handled in composable
  }
}

// Load authorized doctors on mount
onMounted(async () => {
  if (!token.value || !user.value) {
    console.error('User not authenticated, skipping fetch')
    return
  }
  try {
    await fetchAuthorizedDoctors()
  } catch (err) {
    console.error('Failed to load authorized doctors:', err)
  }
})
</script>

<template>
  <UPageCard title="Médicos Autorizados" description="Gerencie médicos autorizados a acessar seus dados."
    variant="subtle">
    <!-- Add Doctor Section -->
    <div class="p-4 bg-elevated/50 rounded-lg border border-border mb-6">
      <h3 class="font-medium mb-3">Adicionar Médico</h3>
      <div class="flex gap-2">
        <UInput v-model="newDoctorCrm" placeholder="Digite o CRM do médico (ex: 12345SP)" class="flex-1"
          :disabled="isAddingDoctor" />
        <UButton icon="i-lucide-user-plus" @click="handleAddDoctor" :loading="isAddingDoctor"
          :disabled="!newDoctorCrm.trim()">
          Compartilhar
        </UButton>
      </div>
      <p class="text-sm text-muted mt-2">
        Informe o CRM do médico para autorizar o acesso aos seus dados.
      </p>
    </div>

    <!-- Authorized Doctors List -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="font-medium">Médicos Autorizados</h3>
      </div>

      <div v-if="authLoading" class="space-y-3">
        <USkeleton v-for="i in 2" :key="i" class="h-16" />
      </div>

      <div v-else-if="authorizedDoctors.length === 0" class="text-center py-8 text-muted">
        <UIcon name="i-lucide-users" class="size-12 mx-auto mb-3 opacity-50" />
        <p>Nenhum médico autorizado ainda.</p>
        <p class="text-sm">Adicione um médico acima para compartilhar seus dados.</p>
      </div>

      <div v-else class="space-y-3">
        <UCard v-for="doctor in authorizedDoctors" :key="doctor.crm" class="p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <UAvatar size="sm" :src="undefined" :alt="doctor.doctor_name">
                <UIcon name="i-lucide-user" class="size-4" />
              </UAvatar>
              <div>
                <p class="font-medium">{{ doctor.doctor_name }}</p>
                <p class="text-sm text-muted">CRM: {{ doctor.crm }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div class="flex flex-col gap-2">
                <div class="flex items-center gap-2">
                  <UBadge :color="doctor.authorized ? 'success' : 'error'" variant="subtle">
                    {{ doctor.authorized ? 'Autorizado' : 'Revogado' }}
                  </UBadge>
                  <USwitch :model-value="doctor.authorized"
                    @update:model-value="handleToggleDoctor(doctor.crm, doctor.doctor_name)" :disabled="authLoading" />
                </div>
                <div v-if="doctor.authorized" class="flex items-center gap-2">
                  <span class="text-sm">Tipo de dados:</span>
                  <URadioGroup 
                    :model-value="doctor.data_type" 
                    @update:model-value="(value) => handleSetDataType(doctor.crm, value)"
                    :options="[
                      { label: 'Fitbit', value: 'fitbit' },
                      { label: 'Simulação', value: 'simulation' }
                    ]" 
                    :disabled="authLoading" 
                  />
                </div>
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </div>

    <!-- Revoke All Authorizations Card -->
    <div v-if="authorizedDoctors.length > 0" class="mt-6 p-4 bg-error/5 rounded-lg border border-error/20">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <UAvatar size="sm" color="error">
            <UIcon name="i-heroicons-exclamation-triangle" class="size-5" />
          </UAvatar>
          <div>
            <h3 class="font-medium text-error">Revogar Todas as Autorizações</h3>
            <p class="text-sm text-muted">Remove o acesso de todos os médicos aos seus dados</p>
          </div>
        </div>
        <UButton color="error" variant="outline" @click="handleRevokeAll">
          Revogar Todos
        </UButton>
      </div>
    </div>
  </UPageCard>
</template>