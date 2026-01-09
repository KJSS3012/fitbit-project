<script setup lang="ts">
import * as z from 'zod'
import type { FormError } from '@nuxt/ui'

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
    <UForm :schema="passwordSchema" :state="password" :validate="validate" class="flex flex-col gap-4 max-w-xs"
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

  <UPageCard title="Excluir Conta"
    description="Não deseja mais usar nosso serviço? Você pode excluir sua conta aqui. Esta ação não é reversível. Todas as informações relacionadas a esta conta serão excluídas permanentemente."
    class="bg-gradient-to-tl from-error/10 from-5% to-default">
    <template #footer>
      <UButton label="Excluir conta" color="error" />
    </template>
  </UPageCard>
</template>
