<script setup lang="ts">
const { login } = useAuth()
const toast = useToast()

const tabs = [
  { label: 'Paciente', value: 'paciente' },
  { label: 'Médico', value: 'medico' }
]

const state = reactive({
  userType: 'paciente',
  cpf: '',
  crm: '',
  password: '',
  rememberMe: false
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
  if (state.userType === 'paciente') {
    if (state.cpf.replace(/\D/g, '').length !== 11) {
      toast.add({
        title: 'CPF inválido',
        description: 'Informe um CPF válido com 11 dígitos',
        color: 'error',
        icon: 'i-heroicons-exclamation-circle'
      })
      return false
    }
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

  if (!state.password || state.password.length < 12) {
    toast.add({
      title: 'Senha inválida',
      description: 'A senha deve ter no mínimo 12 caracteres',
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
    const identifier =
      state.userType === 'paciente'
        ? state.cpf.replace(/\D/g, '')
        : state.crm

    await login(
      state.userType,
      identifier,
      state.password,
      state.rememberMe
    )

    toast.add({
      title: 'Login realizado com sucesso',
      color: 'success',
      icon: 'i-heroicons-check-circle'
    })

    navigateTo('/dashboard')
  } catch (err: any) {
    toast.add({
      title: 'Erro ao entrar',
      description: err?.message || 'Credenciais inválidas',
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
        <h2 class="text-2xl font-semibold">Login</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          Entre com sua conta
        </p>
      </div>
    </template>

    <!-- Tabs -->
    <UTabs
      v-model="state.userType"
      :items="tabs"
      class="mb-4"
    />

    <!-- Form -->
    <UForm class="space-y-4" @submit="onSubmit">
      <!-- Transição -->
      <Transition name="fade-slide" mode="out-in">
        <div :key="state.userType">
          <!-- CPF -->
          <UFormField
            v-if="state.userType === 'paciente'"
            label="CPF"
            required
          >
            <UInput
              v-model="state.cpf"
              placeholder="000.000.000-00"
              size="lg"
              class="w-full"
              maxlength="14"
              @input="formatCPF"
            />
          </UFormField>

          <!-- CRM -->
          <UFormField
            v-else
            label="CRM"
            required
          >
            <UInput
              v-model="state.crm"
              placeholder="Digite seu CRM"
              class="w-full"
              size="lg"
            />
          </UFormField>
        </div>
      </Transition>

      <!-- Senha -->
      <UFormField label="Senha" required>
        <UInput
          v-model="state.password"
          type="password"
          placeholder="••••••••••••"
          class="w-full"
          size="lg"
        />
      </UFormField>

      <div class="flex items-center justify-between">
        <UCheckbox v-model="state.rememberMe" label="Lembrar-me" />
        <UButton variant="link" size="sm" :padded="false">
          Esqueceu a senha?
        </UButton>
      </div>

      <UButton
        type="submit"
        block
        size="lg"
        :loading="loading"
      >
        Entrar
      </UButton>
    </UForm>

    <!-- Footer -->
    <template #footer>
      <div class="text-center text-sm text-gray-500">
        Não tem conta?
        <UButton
          variant="link"
          size="sm"
          :padded="false"
          @click="navigateTo('/auth/register')"
        >
          Registre-se
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
