<script setup lang="ts">
import { useFitbitAuth } from '~/composables/useFitbitAuth'
import { useFitbitData } from '~/composables/useFitbitData'

const { isFitbitConnected, connectFitbit, disconnectFitbit, isConnecting } = useFitbitAuth()
const { isSimulationMode, enableFitbitMode, enableSimulationMode } = useFitbitData()
</script>

<template>
  <div class="space-y-2">
    <div class="flex gap-2">
      <UButton v-if="!isFitbitConnected" label="Conectar Fitbit" icon="i-simple-icons-fitbit" color="primary"
        variant="ghost" :loading="isConnecting" @click="connectFitbit" />
      <UButton v-else label="Desconectar Fitbit" icon="i-lucide-unplug" color="error" variant="ghost"
        @click="disconnectFitbit" />
    </div>

    <div class="flex gap-2">
      <UButton :label="isFitbitConnected ? 'Fitbit (Ativo)' : 'Ativar Fitbit'"
        :icon="isFitbitConnected ? 'i-lucide-check-circle' : 'i-simple-icons-fitbit'"
        :color="isFitbitConnected ? 'primary' : 'neutral'" :variant="isFitbitConnected ? 'soft' : 'ghost'" block
        class="justify-start" :disabled="!isFitbitConnected" @click="enableFitbitMode" />
      <UButton :label="isSimulationMode ? 'Simulação (Ativa)' : 'Ativar Simulação'"
        :icon="isSimulationMode ? 'i-lucide-check-circle' : 'i-lucide-flask-conical'"
        :color="isSimulationMode ? 'success' : 'neutral'" :variant="isSimulationMode ? 'soft' : 'ghost'" block
        class="justify-start" @click="enableSimulationMode" />
    </div>
  </div>
</template>
