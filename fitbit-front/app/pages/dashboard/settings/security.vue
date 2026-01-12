<script setup lang="ts">
import * as z from 'zod'
import type { FormError } from '@nuxt/ui'
import { useFitbitAuth } from '~/composables/useFitbitAuth'
import { useAuthorization } from '~/composables/useAuthorization'
import FitbitConnect from '~/components/shared/FitbitConnect.vue'

const passwordSchema = z.object({
  current: z.string().min(8, 'Deve ter pelo menos 8 caracteres'),
  new: z.string().min(8, 'Deve ter pelo menos 8 caracteres')
})

type PasswordSchema = z.output<typeof passwordSchema>

const password = reactive<Partial<PasswordSchema>>({
  current: undefined,
  new: undefined
})

const validate = (state: Partial<PasswordSchema>): FormError[] => {
  const errors: FormError[] = []
  if (state.current && state.new && state.current === state.new) {
    errors.push({ name: 'new', message: 'As senhas devem ser diferentes' })
  }
  return errors
}

const toast = useToast()

// Fitbit connection + Authorization (doctors)
const {
  authorizedDoctors,
  fetchAuthorizedDoctors,
  toggleDoctorAuthorization,
  addDoctorAuthorization,
  revokeAllAuthorizations,
  isLoading: authLoading
} = useAuthorization()

const { checkFitbitStatus } = useFitbitAuth()

const newDoctorCrm = ref('')
const isAddingDoctor = ref(false)

const handleAddDoctor = async () => {
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
  try {
    await toggleDoctorAuthorization(doctorCrm, doctorName)
    // Refresh the list after toggling
    await fetchAuthorizedDoctors()
  } catch (err) {
    // toast handled in composable
  }
}

const handleRevokeAll = async () => {
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
  try {
    await fetchAuthorizedDoctors()
    await checkFitbitStatus()
  } catch (err) {
    console.error('Failed to load authorized doctors:', err)
  }
})

async function onSubmit() {
  // TODO: Implementar mudança de senha
  // await $fetch('/api/auth/change-password', {
  //   method: 'POST',
  //   body: password
  // })

  toast.add({
    title: 'Senha atualizada',
    description: 'Sua senha foi alterada com sucesso.',
    icon: 'i-lucide-check',
    color: 'success'
  })

  password.current = undefined
  password.new = undefined
}
</script>

<template>
  <UPageCard title="Senha" description="Confirme sua senha atual antes de definir uma nova." variant="subtle">
    <UForm :schema="passwordSchema" :state="password" :validate="validate" class="flex flex-col gap-4"
      @submit="onSubmit">
      <UFormField name="current">
        <UInput v-model="password.current" type="password" placeholder="Senha atual" class="w-full" />
      </UFormField>

      <UFormField name="new">
        <UInput v-model="password.new" type="password" placeholder="Nova senha" class="w-full" />
      </UFormField>

      <UButton label="Atualizar" class="w-fit" type="submit" />
    </UForm>
  </UPageCard>

  <!-- Add / Share with Doctor -->
  <UPageCard title="Médicos Autorizados" description="Gerencie médicos autorizados a acessar seus dados."
    variant="subtle">
    <!-- Fitbit Connection -->
    <div class="mb-6">
      <FitbitConnect />
    </div>
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
              <UBadge :color="doctor.authorized ? 'success' : 'error'" variant="subtle">
                {{ doctor.authorized ? 'Autorizado' : 'Revogado' }}
              </UBadge>
              <USwitch :model-value="doctor.authorized"
                @update:model-value="handleToggleDoctor(doctor.crm, doctor.doctor_name)" :disabled="authLoading" />
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
