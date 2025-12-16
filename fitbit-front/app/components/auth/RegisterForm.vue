<script setup lang="ts">
import { register as registerAPI } from '~/services/api'

const toast = useToast()

const tabs = [
  { label: 'Paciente', value: 'paciente' },
  { label: 'Médico', value: 'medico' }
]

const state = reactive({
  userType: 'paciente',
  name: '',
  cpf: '',
  crm: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false
})

const loading = ref(false)

const formatCPF = (event: Event) => {
  const input = event.target as HTMLInputElement
  let value = input.value.replace(/\D/g, '').slice(0, 11)

  if (value.length > 9)
    value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
  else if (value.length > 6)
    value = value.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3')
  else if (value.length > 3)
    value = value.replace(/(\d{3})(\d{1,3})/, '$1.$2')

  state.cpf = value
}

const validateForm = () => {
  if (!state.name.trim()) {
    toast.add({
      title: 'Nome obrigatório',
      description: 'Informe seu nome completo',
      color: 'error',
      icon: 'i-heroicons-exclamation-circle'
    })
    return false
  }

  if (state.cpf.replace(/\D/g, '').length !== 11) {
    toast.add({
      title: 'CPF inválido',
      description: 'Informe um CPF válido com 11 dígitos',
      color: 'error',
      icon: 'i-heroicons-exclamation-circle'
    })
    return false
  }

  if (state.userType === 'medico' && !state.crm.trim()) {
    toast.add({
      title: 'CRM obrigatório',
      description: 'Informe seu CRM para continuar',
      color: 'error',
      icon: 'i-heroicons-exclamation-circle'
    })
    return false
  }

  if (state.password.length < 12) {
    toast.add({
      title: 'Senha fraca',
      description: 'A senha deve ter no mínimo 12 caracteres',
      color: 'error',
      icon: 'i-heroicons-exclamation-circle'
    })
    return false
  }

  if (state.password !== state.confirmPassword) {
    toast.add({
      title: 'Senhas não coincidem',
      description: 'A confirmação deve ser igual à senha',
      color: 'error',
      icon: 'i-heroicons-exclamation-circle'
    })
    return false
  }

  if (!state.acceptTerms) {
    toast.add({
      title: 'Termos obrigatórios',
      description: 'Você precisa aceitar os termos de uso',
      color: 'error',
      icon: 'i-heroicons-exclamation-circle'
    })
    return false
  }

  return true
}

const onSubmit = async () => {
  if (!validateForm()) return

  loading.value = true

  try {
    await registerAPI({
      user_type: state.userType,
      cpf: state.cpf.replace(/\D/g, ''),
      name: state.name,
      password: state.password,
      crm: state.userType === 'medico' ? state.crm : undefined
    })


    toast.add({
      title: 'Conta criada com sucesso',
      description: 'Redirecionando para o login...',
      color: 'success',
      icon: 'i-heroicons-check-circle'
    })

    setTimeout(() => navigateTo('/auth/login'), 1500)
  } catch (err: any) {
    toast.add({
      title: 'Erro ao criar conta',
      description: err?.message || 'Tente novamente mais tarde',
      color: 'error',
      icon: 'i-heroicons-x-circle'
    })
  } finally {
    loading.value = false
  }
}
</script>



<template>
  <UCard class="w-full max-w-md">
    <!-- Header -->
    <template #header>
      <div class="text-center space-y-1">
        <h2 class="text-2xl font-semibold">Criar Conta</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          Registre-se para começar
        </p>
      </div>
    </template>

    <!-- Tabs -->
    <UTabs v-model="state.userType" :items="tabs" class="mb-4" />

    <!-- Form -->
    <UForm class="space-y-4" @submit="onSubmit">
      <!-- Campos dinâmicos -->
      <Transition name="fade-slide" mode="out-in">
        <div :key="state.userType" class="space-y-4">
          <!-- Nome -->
          <UFormField label="Nome Completo" required>
            <UInput v-model="state.name" placeholder="Digite seu nome completo" size="lg" class="w-full" />
          </UFormField>

          <!-- CPF -->
          <UFormField label="CPF" required>
            <UInput v-model="state.cpf" placeholder="000.000.000-00" size="lg" class="w-full" maxlength="14"
              @input="formatCPF" />
          </UFormField>

          <!-- CRM -->
          <UFormField v-if="state.userType === 'medico'" label="CRM" required>
            <UInput v-model="state.crm" placeholder="Digite seu CRM" size="lg" class="w-full" />
          </UFormField>
        </div>
      </Transition>

      <!-- Senha -->
      <UFormField label="Senha" required>
        <UInput v-model="state.password" type="password" placeholder="••••••••••••" class="w-full" size="lg" />

        <template #description>
          <span class="text-xs text-muted">
            Mínimo 12 caracteres com maiúscula, minúscula, número e caractere especial
          </span>
        </template>
      </UFormField>

      <!-- Confirmar senha -->
      <UFormField label="Confirmar Senha" required>
        <UInput v-model="state.confirmPassword" type="password" placeholder="••••••••••••" class="w-full" size="lg" />
      </UFormField>

      <!-- Termos -->
      <UCheckbox v-model="state.acceptTerms" label="Aceito os termos de uso e política de privacidade" />

      <!-- Submit -->
      <UButton type="submit" block size="lg" :loading="loading" :disabled="loading || !state.acceptTerms">
        Criar Conta
      </UButton>
    </UForm>

    <!-- Footer -->
    <template #footer>
      <div class="text-center text-sm text-gray-500">
        Já tem uma conta?
        <UButton variant="link" size="sm" :padded="false" @click="navigateTo('/auth/login')">
          Faça login
        </UButton>
      </div>
    </template>
  </UCard>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
</style>
