<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent, FormError } from '@nuxt/ui'

const { user, token } = useAuth()
const config = useRuntimeConfig()
const toast = useToast()

// Initialize Fitbit auth to handle OAuth redirects
const { checkFitbitStatus } = useFitbitAuth()

// Check Fitbit status on page load (handles OAuth redirects)
onMounted(async () => {
  await checkFitbitStatus()
})

const profileSchema = z.object({
  name: z.string().min(3, 'Nome deve ter pelo menos 3 caracteres')
})

type ProfileSchema = z.output<typeof profileSchema>

const profile = reactive<Partial<ProfileSchema>>({
  name: user.value?.name || ''
})

const passwordSchema = z.object({
  current: z.string().min(8, 'Deve ter pelo menos 8 caracteres'),
  new: z.string().min(8, 'Deve ter pelo menos 8 caracteres')
})

type PasswordSchema = z.output<typeof passwordSchema>

const password = reactive<Partial<PasswordSchema>>({
  current: undefined,
  new: undefined
})

const validatePassword = (state: Partial<PasswordSchema>): FormError[] => {
  const errors: FormError[] = []
  if (state.current && state.new && state.current === state.new) {
    errors.push({ name: 'new', message: 'As senhas devem ser diferentes' })
  }
  return errors
}

const isLoading = ref(false)

async function onSubmit(event: FormSubmitEvent<ProfileSchema>) {
  isLoading.value = true

  try {
    const updateData: { name?: string } = {}

    if (event.data.name && event.data.name !== user.value?.name) {
      updateData.name = event.data.name
    }

    if (Object.keys(updateData).length === 0) {
      toast.add({
        title: 'Nenhuma alteração',
        description: 'Você não modificou nenhum campo',
        color: 'neutral'
      })
      return
    }

    await $fetch(`${config.public.apiBase}/user/me`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${token.value}`
      },
      body: updateData
    })

    toast.add({
      title: 'Dados atualizados',
      description: 'Suas informações foram alteradas com sucesso',
      color: 'success',
      icon: 'i-lucide-check'
    })

  } catch (error: any) {
    toast.add({
      title: 'Erro ao atualizar',
      description: error.data?.detail || 'Tente novamente',
      color: 'error',
      icon: 'i-lucide-alert-circle'
    })
  } finally {
    isLoading.value = false
  }
}

async function onPasswordSubmit() {
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
  <UForm id="settings-general" :schema="profileSchema" :state="profile" @submit="onSubmit">
    <UPageCard title="Perfil" description="Atualize seu nome. CPF/CRM não podem ser alterados." variant="naked"
      orientation="horizontal" class="mb-4">
      <UButton form="settings-general" label="Salvar alterações" color="neutral" type="submit" :loading="isLoading"
        class="w-fit lg:ms-auto" />
    </UPageCard>

    <UPageCard variant="subtle">
      <UFormField name="name" label="Nome Completo" description="Seu nome será exibido no dashboard." required
        class="flex max-sm:flex-col justify-between items-start gap-4">
        <UInput v-model="profile.name" autocomplete="off" placeholder="Ex: João Silva" />
      </UFormField>
    </UPageCard>
  </UForm>

  <UPageCard title="Senha" description="Confirme sua senha atual antes de definir uma nova." variant="subtle" class="mt-6">
    <UForm :schema="passwordSchema" :state="password" :validate="validatePassword" class="flex flex-col gap-4"
      @submit="onPasswordSubmit">
      <UFormField name="current">
        <UInput v-model="password.current" type="password" placeholder="Senha atual" class="w-full" />
      </UFormField>

      <UFormField name="new">
        <UInput v-model="password.new" type="password" placeholder="Nova senha" class="w-full" />
      </UFormField>

      <UButton label="Atualizar" class="w-fit" type="submit" />
    </UForm>
  </UPageCard>
</template>