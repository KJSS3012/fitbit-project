<script setup lang="ts">


const runtimeConfig = useRuntimeConfig()
const loading = ref(false)
const connected = ref(false)
const data = ref<any>(null)

const connectFitbit = () => {
  window.location.href = `${runtimeConfig.public.apiBase}/fitbit/auth`
}

const loadDashboard = async () => {
  try {
    loading.value = true
    data.value = await $fetch('/fitbit/dashboard', {
      baseURL: runtimeConfig.public.apiBase as string,
      credentials: 'include'
    })
    connected.value = true
  } catch (err) {
    connected.value = false
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>

<template>
  <div class="p-6 space-y-6">
    <h1 class="text-2xl font-semibold">Dashboard Fitbit</h1>

    <UCard v-if="!connected">
      <div class="flex flex-col items-center gap-4">
        <p class="text-gray-500">
          Conecte sua conta Fitbit para visualizar seus dados de saúde.
        </p>

        <UButton icon="i-simple-icons-fitbit" size="lg" color="primary" @click="connectFitbit">
          Conectar com Fitbit
        </UButton>
      </div>
    </UCard>

    <UCard v-else>
      <template #header>
        <h2 class="text-lg font-medium">Resumo</h2>
      </template>

      <div v-if="loading">
        <USkeleton class="h-24 w-full" />
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <UCard>
          <h3 class="font-medium mb-2">Perfil</h3>
          <p>{{ data.profile.user.fullName }}</p>
        </UCard>

        <UCard>
          <h3 class="font-medium mb-2">Atividade</h3>
          <p>Passos: {{ data.activity.summary.steps }}</p>
        </UCard>

        <UCard>
          <h3 class="font-medium mb-2">Frequência Cardíaca</h3>
          <p>
            Média:
            {{ data.heartrate['activities-heart'][0].value.restingHeartRate }}
          </p>
        </UCard>

        <UCard>
          <h3 class="font-medium mb-2">Sono</h3>
          <p>
            Total:
            {{ data.sleep.summary.totalMinutesAsleep }} minutos
          </p>
        </UCard>
      </div>
    </UCard>
  </div>
</template>
