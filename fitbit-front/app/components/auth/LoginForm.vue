<script setup lang="ts">
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { loginSchema } from '~/schemas/auth.schema'
import type { TabsItem } from '@nuxt/ui/runtime/components/Tabs.vue.js'

const { login } = useAuth()
const toast = useToast()

const tabs: TabsItem[] = [
  { label: 'Patient', value: 'paciente' },
  { label: 'Doctor', value: 'medico' }
]

const { handleSubmit, errors, isSubmitting } = useForm({
  validationSchema: toTypedSchema(loginSchema),
  initialValues: {
    userType: 'paciente',
    rememberMe: false,
    cpf: '',
    crm: ''
  }
})

const { value: userType } = useField<'paciente' | 'medico'>('userType')
const { value: cpf } = useField<string>('cpf')
const { value: crm } = useField<string>('crm')
const { value: password } = useField<string>('password')
const { value: rememberMe } = useField<boolean>('rememberMe')

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
    const identifier =
      values.userType === 'paciente'
        ? values.cpf?.replace(/\D/g, '') || ''
        : values.crm || ''

    await login(
      values.userType,
      identifier,
      values.password,
      values.rememberMe || false
    )

    toast.add({
      title: 'Login successful',
      color: 'success',
      icon: 'i-heroicons-check-circle'
    })

    navigateTo('/dashboard')
  } catch (err: any) {
    toast.add({
      title: 'Login failed',
      description: err?.message || 'Invalid credentials',
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
        <h2 class="text-2xl font-semibold">Login</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          Sign in to your account
        </p>
      </div>
    </template>

    <UTabs v-model="userType" :items="tabs" class="mb-4" />

    <UForm class="space-y-4" @submit="onSubmit">
      <Transition name="fade-slide" mode="out-in">
        <div :key="userType">
          <UFormField v-if="userType === 'paciente'" label="CPF" required :error="errors.cpf">
            <UInput v-model="cpf" placeholder="000.000.000-00" size="lg" class="w-full" maxlength="14"
              @input="formatCPF" />
          </UFormField>

          <UFormField v-else label="CRM" required :error="errors.crm">
            <UInput v-model="crm" placeholder="Enter your CRM" size="lg" class="w-full" />
          </UFormField>
        </div>
      </Transition>

      <UFormField label="Password" required :error="errors.password">
        <UInput v-model="password" type="password" placeholder="••••••••••••" size="lg" class="w-full" />
      </UFormField>

      <div class="flex items-center justify-between">
        <UCheckbox v-model="rememberMe" label="Remember me" />
        <UButton variant="link" size="sm" :padded="false">
          Forgot password?
        </UButton>
      </div>

      <UButton type="submit" block size="lg" :loading="isSubmitting" :disabled="isSubmitting">
        Sign In
      </UButton>
    </UForm>

    <template #footer>
      <div class="text-center text-sm text-gray-500">
        Don't have an account?
        <UButton variant="link" size="sm" :padded="false" @click="navigateTo('/auth/register')">
          Sign up
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
