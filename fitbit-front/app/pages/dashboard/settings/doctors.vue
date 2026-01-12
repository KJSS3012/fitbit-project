<script setup lang="ts">
import { useAuthorization } from '~/composables/useAuthorization'

/**
 * PB11: Patient controls which doctors can access their health data.
 * Scenarios: 1(grant), 2(revoke), 3(audit error), 4(empty state)
 */
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const { user, isDoctor } = useAuth()
const { authorizedDoctors, isLoading, fetchAuthorizedDoctors, toggleDoctorAuthorization, addDoctorAuthorization } = useAuthorization()

const newDoctorCrm = ref('')
const isAddingDoctor = ref(false)

// Redirect doctors to patients page
onMounted(async () => {
  if (isDoctor.value) {
    navigateTo('/patients')
    return
  }

  await fetchAuthorizedDoctors()
})

const handleToggleAuthorization = async (doctor: any) => {
  try {
    await toggleDoctorAuthorization(doctor.crm, doctor.doctor_name)
  } catch (error) {
    // Error handled in composable with toast
    console.error('Toggle failed:', error)
  }
}

const handleAddDoctor = async () => {
  if (!newDoctorCrm.value.trim()) {
    return
  }

  isAddingDoctor.value = true

  try {
    await addDoctorAuthorization(newDoctorCrm.value.trim())
    newDoctorCrm.value = ''
  } catch (error) {
    // Error handled in composable
  } finally {
    isAddingDoctor.value = false
  }
}
</script>

<template>
  <UPageCard title="Médicos Autorizados" description="Controle quais médicos podem visualizar seus dados de saúde."
    variant="subtle">
    <div class="space-y-6">
      <!-- Add New Doctor -->
      <div class="p-4 bg-elevated/50 rounded-lg border border-border">
        <h3 class="font-medium mb-3">Adicionar Médico</h3>
        <div class="flex gap-2">
          <UInput v-model="newDoctorCrm" placeholder="Digite o CRM do médico (ex: 12345SP)" class="flex-1"
            :disabled="isAddingDoctor" />
          <UButton icon="i-lucide-user-plus" @click="handleAddDoctor" :loading="isAddingDoctor"
            :disabled="!newDoctorCrm.trim()">
            Adicionar
          </UButton>
        </div>
        <p class="text-sm text-muted mt-2">
          Informe o CRM do médico que você deseja autorizar a visualizar seus dados
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading && authorizedDoctors.length === 0" class="space-y-3">
        <USkeleton v-for="i in 3" :key="i" class="h-20" />
      </div>

      <!-- PB11 Scenario 4: Empty State -->
      <div v-else-if="authorizedDoctors.length === 0" class="text-center py-12">
        <UIcon name="i-lucide-user-x" class="size-16 text-muted mx-auto mb-4" />
        <h3 class="text-lg font-semibold mb-2">Nenhum médico vinculado</h3>
        <p class="text-muted">
          Você ainda não autorizou nenhum médico a visualizar seus dados.<br>
          Use o campo acima para adicionar um médico pelo CRM.
        </p>
      </div>

      <!-- Doctors List -->
      <div v-else class="space-y-3">
        <div v-for="doctor in authorizedDoctors" :key="doctor.crm"
          class="flex items-center justify-between p-4 bg-elevated/50 rounded-lg border border-border hover:border-primary/30 transition-colors">
          <div class="flex items-center gap-3">
            <div class="p-2 rounded-full" :class="doctor.authorized ? 'bg-success/10' : 'bg-neutral/10'">
              <UIcon :name="doctor.authorized ? 'i-lucide-user-check' : 'i-lucide-user-x'" class="size-5"
                :class="doctor.authorized ? 'text-success' : 'text-muted'" />
            </div>
            <div>
              <p class="font-medium">{{ doctor.doctor_name }}</p>
              <p class="text-sm text-muted">CRM: {{ doctor.crm }}</p>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <div class="text-right">
              <p class="text-sm font-medium" :class="doctor.authorized ? 'text-success' : 'text-muted'">
                {{ doctor.authorized ? 'Compartilhamento Ativo' : 'Compartilhamento Inativo' }}
              </p>
              <p class="text-xs text-muted">
                {{ doctor.authorized ? 'Pode visualizar seus dados' : 'Sem acesso aos dados' }}
              </p>
            </div>

            <!-- PB11 Scenarios 1 & 2: Toggle Authorization -->
            <USwitch v-model="doctor.authorized" @update:model-value="handleToggleAuthorization(doctor)"
              :disabled="isLoading" />
          </div>
        </div>
      </div>

      <!-- Info Alert -->
      <div class="p-4 bg-info/5 rounded-lg border border-info/20">
        <div class="flex gap-3">
          <UIcon name="i-lucide-shield-check" class="size-5 text-info shrink-0 mt-0.5" />
          <div class="text-sm">
            <p class="font-medium text-info mb-1">Privacidade e Controle</p>
            <p class="text-muted">
              Você tem controle total sobre quem pode visualizar seus dados de saúde.
              Ao ativar o compartilhamento, o médico poderá visualizar suas métricas sincronizadas do Fitbit.
              Você pode revogar o acesso a qualquer momento.
            </p>
          </div>
        </div>
      </div>
    </div>
  </UPageCard>
</template>
