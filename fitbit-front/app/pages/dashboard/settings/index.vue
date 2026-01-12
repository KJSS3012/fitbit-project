<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

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
  name: z.string().min(3, 'Nome deve ter pelo menos 3 caracteres'),
  password: z.string().min(12, 'Senha deve ter pelo menos 12 caracteres').optional().or(z.literal(''))
})

type ProfileSchema = z.output<typeof profileSchema>

const profile = reactive<Partial<ProfileSchema>>({
  name: user.value?.name || '',
  password: ''
})

const isLoading = ref(false)

async function onSubmit(event: FormSubmitEvent<ProfileSchema>) {
  isLoading.value = true

  try {
    const updateData: { name?: string; password?: string } = {}

    if (event.data.name && event.data.name !== user.value?.name) {
      updateData.name = event.data.name
    }

    if (event.data.password && event.data.password.length > 0) {
      updateData.password = event.data.password
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

    if (updateData.password) {
      profile.password = ''
    }
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
</script>

<template>
  <UForm id="settings-general" :schema="profileSchema" :state="profile" @submit="onSubmit">
    <UPageCard title="Perfil" description="Atualize seu nome e senha. CPF/CRM não podem ser alterados." variant="naked"
      orientation="horizontal" class="mb-4">
      <UButton form="settings-general" label="Salvar alterações" color="neutral" type="submit" :loading="isLoading"
        class="w-fit lg:ms-auto" />
    </UPageCard>

    <UPageCard variant="subtle">
      <UFormField name="name" label="Nome Completo" description="Seu nome será exibido no dashboard." required
        class="flex max-sm:flex-col justify-between items-start gap-4">
        <UInput v-model="profile.name" autocomplete="off" placeholder="Ex: João Silva" />
      </UFormField>

      <USeparator />

      <UFormField name="password" label="Nova Senha"
        description="Deixe em branco para manter a senha atual. Mínimo 12 caracteres."
        class="flex max-sm:flex-col justify-between items-start gap-4">
        <UInput v-model="profile.password" type="password" autocomplete="new-password" placeholder="••••••••••••" />
      </UFormField>
    </UPageCard>
  </UForm>
</template>
