<script setup lang="ts">
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { registerSchema } from '~/schemas/auth.schema'
import type { TabsItem } from '@nuxt/ui/runtime/components/Tabs.vue.js'

const { register } = useAuth()
const toast = useToast()

const tabs: TabsItem[] = [
  { label: 'Paciente', value: 'paciente' },
  { label: 'Médico', value: 'medico' }
]

const { handleSubmit, errors, isSubmitting } = useForm({
  validationSchema: toTypedSchema(registerSchema),
  initialValues: {
    userType: 'paciente',
    acceptTerms: false,
    crm: ''
  }
})

const { value: userType } = useField<'paciente' | 'medico'>('userType')
const { value: name } = useField<string>('name')
const { value: cpf } = useField<string>('cpf')
const { value: crm } = useField<string>('crm')
const { value: password } = useField<string>('password')
const { value: confirmPassword } = useField<string>('confirmPassword')
const { value: acceptTerms } = useField<boolean>('acceptTerms')

const formatCPF = (event: Event) => {
  const input = event.target as HTMLInputElement
  let value = input.value.replace(/\D/g, '').slice(0, 11)

  if (value.length > 9)
    value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
  else if (value.length > 6)
    value = value.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3')
  else if (value.length > 3)
    value = value.replace(/(\d{3})(\d{1,3})/, '$1.$2')

  cpf.value = value
}

const submitHandler = handleSubmit(async (values) => {
  try {
    await register({
      user_type: values.userType,
      name: values.name,
      cpf: values.cpf.replace(/\D/g, ''),
      password: values.password,
      crm: values.userType === 'medico' ? values.crm : undefined
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
      title: 'Falha ao criar conta',
      description: err?.message || 'Tente novamente mais tarde',
      color: 'error',
      icon: 'i-heroicons-x-circle'
    })
  }
})

const onSubmit = async () => {
  await submitHandler()
}
</script>

<template>
  <UCard class="w-full max-w-md">
    <template #header>
      <div class="text-center space-y-1">
        <h2 class="text-2xl font-semibold">Criar Conta</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          Cadastre-se para começar
        </p>
      </div>
    </template>

    <UTabs v-model="userType" :items="tabs" class="mb-4" />

    <UForm class="space-y-4" @submit="onSubmit">
      <Transition name="fade-slide" mode="out-in">
        <div :key="userType" class="space-y-4">
          <UFormField label="Nome Completo" required :error="errors.name">
            <UInput v-model="name" size="lg" class="w-full" />
          </UFormField>

          <UFormField label="CPF" required :error="errors.cpf">
            <UInput v-model="cpf" size="lg" class="w-full" maxlength="14" @input="formatCPF" />
          </UFormField>

          <UFormField v-if="userType === 'medico'" label="CRM" required :error="errors.crm">
            <UInput v-model="crm" size="lg" class="w-full" />
          </UFormField>
        </div>
      </Transition>

      <UFormField label="Senha" required :error="errors.password">
        <UInput v-model="password" type="password" size="lg" class="w-full" />
      </UFormField>

      <UFormField label="Confirmar Senha" required :error="errors.confirmPassword">
        <UInput v-model="confirmPassword" type="password" size="lg" class="w-full" />
      </UFormField>

      <div class="space-y-1">
        <UCheckbox v-model="acceptTerms" label="Aceito os termos de uso" />
        <p v-if="errors.acceptTerms" class="text-sm text-red-500">
          {{ errors.acceptTerms }}
        </p>
      </div>

      <UButton type="submit" block size="lg" :loading="isSubmitting" :disabled="isSubmitting">
        Criar Conta
      </UButton>
    </UForm>
    <template #footer>
      <div class="text-center text-sm text-gray-500">
        Já tem uma conta?
        <UButton variant="link" size="sm" :padded="false" @click="navigateTo('/auth/login')">
          Entrar
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
