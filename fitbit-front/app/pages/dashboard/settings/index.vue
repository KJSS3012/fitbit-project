<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

const { user } = useAuth()

const profileSchema = z.object({
  name: z.string().min(2, 'Nome muito curto'),
  email: z.string().email('Email inválido'),
  cpf: z.string().min(11, 'CPF inválido')
})

type ProfileSchema = z.output<typeof profileSchema>

const profile = reactive<Partial<ProfileSchema>>({
  name: user.value?.name || '',
  email: user.value?.email || '',
  cpf: ''
})

const toast = useToast()

async function onSubmit(event: FormSubmitEvent<ProfileSchema>) {
  // TODO: Implementar atualização de perfil
  // await $fetch('/api/profile/update', {
  //   method: 'PUT',
  //   body: event.data
  // })

  toast.add({
    title: 'Sucesso',
    description: 'Suas configurações foram atualizadas.',
    icon: 'i-lucide-check',
    color: 'success'
  })
  console.log(event.data)
}
</script>

<template>
  <UForm id="settings-general" :schema="profileSchema" :state="profile" @submit="onSubmit">
    <UPageCard title="Perfil" description="Informações pessoais que serão exibidas em sua conta." variant="naked"
      orientation="horizontal" class="mb-4">
      <UButton form="settings-general" label="Salvar alterações" color="neutral" type="submit"
        class="w-fit lg:ms-auto" />
    </UPageCard>

    <UPageCard variant="subtle">
      <UFormField name="name" label="Nome" description="Seu nome completo." required
        class="flex max-sm:flex-col justify-between items-start gap-4">
        <UInput v-model="profile.name" autocomplete="off" />
      </UFormField>

      <USeparator />

      <UFormField name="email" label="Email" description="Usado para login e comunicações importantes." required
        class="flex max-sm:flex-col justify-between items-start gap-4">
        <UInput v-model="profile.email" type="email" autocomplete="off" />
      </UFormField>

      <USeparator />

      <UFormField name="cpf" label="CPF" description="Seu CPF cadastrado no sistema." required
        class="flex max-sm:flex-col justify-between items-start gap-4">
        <UInput v-model="profile.cpf" placeholder="000.000.000-00" autocomplete="off" disabled />
      </UFormField>
    </UPageCard>
  </UForm>
</template>
