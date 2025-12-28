<script setup lang="ts">
const runtimeConfig = useRuntimeConfig()
const toast = useToast()

const loading = ref(false)
const connected = ref(false)

const connectFitbit = () => {
  window.location.href = `${runtimeConfig.public.apiBase}/fitbit/auth`
}

const disconnectFitbit = async () => {
  loading.value = true
  try {
    // TODO: Implementar desconexão do Fitbit
    // await $fetch('/api/fitbit/disconnect', {
    //   baseURL: runtimeConfig.public.apiBase,
    //   method: 'POST',
    //   credentials: 'include'
    // })

    await new Promise(resolve => setTimeout(resolve, 1000))
    connected.value = false

    toast.add({
      title: 'Desconectado',
      description: 'Sua conta Fitbit foi desconectada.',
      icon: 'i-lucide-check',
      color: 'success'
    })
  } catch (error) {
    toast.add({
      title: 'Erro',
      description: 'Não foi possível desconectar sua conta Fitbit.',
      icon: 'i-lucide-alert-circle',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

// Estado de compartilhamento com médico
const sharingEnabled = ref(true)

const toggleSharing = async () => {
  // TODO: Implementar toggle de compartilhamento
  // await $fetch('/api/sharing/toggle', {
  //   method: 'POST',
  //   body: { enabled: sharingEnabled.value }
  // })

  toast.add({
    title: sharingEnabled.value ? 'Compartilhamento ativado' : 'Compartilhamento desativado',
    description: sharingEnabled.value
      ? 'Seu médico agora pode visualizar seus dados.'
      : 'Seu médico não pode mais visualizar seus dados.',
    icon: 'i-lucide-check',
    color: 'success'
  })
}
</script>

<template>
  <UPageCard title="Conexão com Fitbit"
    description="Gerencie a conexão com sua conta Fitbit para sincronizar seus dados de saúde." variant="subtle">
    <div class="space-y-4">
      <div class="flex items-center justify-between p-4 bg-elevated/50 rounded-lg">
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-full bg-primary/10">
            <UIcon name="i-simple-icons-fitbit" class="size-5 text-primary" />
          </div>
          <div>
            <p class="font-medium">Conta Fitbit</p>
            <p class="text-sm text-muted">{{ connected ? 'Conectada' : 'Não conectada' }}</p>
          </div>
        </div>
        <UButton v-if="!connected" icon="i-simple-icons-fitbit" color="primary" @click="connectFitbit">
          Conectar
        </UButton>
        <UButton v-else icon="i-lucide-unplug" color="error" variant="outline" @click="disconnectFitbit"
          :loading="loading">
          Desconectar
        </UButton>
      </div>

      <div class="p-4 bg-info/5 rounded-lg border border-info/20">
        <div class="flex gap-3">
          <UIcon name="i-lucide-info" class="size-5 text-info shrink-0 mt-0.5" />
          <div class="text-sm">
            <p class="font-medium text-info mb-1">Sobre a sincronização</p>
            <p class="text-muted">
              Ao conectar sua conta Fitbit, sincronizamos automaticamente seus dados de passos,
              frequência cardíaca e sono. Os dados são atualizados periodicamente.
            </p>
          </div>
        </div>
      </div>
    </div>
  </UPageCard>

  <UPageCard title="Compartilhamento com Médico"
    description="Controle se seu médico pode visualizar seus dados de saúde." variant="subtle">
    <div class="space-y-4">
      <div class="flex items-center justify-between p-4 bg-elevated/50 rounded-lg">
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-full bg-success/10">
            <UIcon name="i-lucide-user-check" class="size-5 text-success" />
          </div>
          <div>
            <p class="font-medium">Compartilhamento Ativo</p>
            <p class="text-sm text-muted">
              {{ sharingEnabled ? 'Seu médico pode visualizar seus dados' : 'Compartilhamento desativado' }}
            </p>
          </div>
        </div>
        <USwitch v-model="sharingEnabled" @update:model-value="toggleSharing" />
      </div>

      <div v-if="sharingEnabled" class="p-4 bg-warning/5 rounded-lg border border-warning/20">
        <div class="flex gap-3">
          <UIcon name="i-lucide-shield-alert" class="size-5 text-warning shrink-0 mt-0.5" />
          <div class="text-sm">
            <p class="font-medium text-warning mb-1">Privacidade</p>
            <p class="text-muted">
              Ao ativar o compartilhamento, seu médico poderá visualizar todos os seus dados de saúde
              sincronizados do Fitbit. Você pode desativar a qualquer momento.
            </p>
          </div>
        </div>
      </div>
    </div>
  </UPageCard>
</template>
