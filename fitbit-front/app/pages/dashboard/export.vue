<script setup lang="ts">
import { sub, startOfDay, endOfDay } from 'date-fns'
import type { Range } from '~/types/dashboard'
import type { ExportFormat } from '~/composables/useExport'

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const router = useRouter()
const route = useRoute()
const { user, isDoctor } = useAuth()
const { exportData, isExporting } = useExport()
const { authorizedPatients, fetchAuthorizedPatients } = useDoctorPatients()

const selectedFormat = ref<ExportFormat>('pdf')
const range = ref<Range>({
  start: startOfDay(sub(new Date(), { days: 6 })),
  end: endOfDay(new Date())
})

// Get patientId from query or use current user
const patientId = computed(() => route.query.patientId as string || user.value?.id || '')

// For doctors, patient name might be different
const patientName = computed(() => {
  if (isDoctor.value && route.query.patientId) {
    const patient = authorizedPatients.value.find(p => p.cpf === route.query.patientId)
    return patient?.name || 'Paciente'
  }
  return user.value?.name || 'Paciente'
})

onMounted(async () => {
  if (isDoctor.value) {
    await fetchAuthorizedPatients()
  }
})

const formatTabs = [
  {
    label: 'PDF',
    slot: 'pdf',
    icon: 'i-lucide-file-text'
  },
  {
    label: 'CSV',
    slot: 'csv',
    icon: 'i-lucide-table'
  },
  {
    label: 'JSON',
    slot: 'json',
    icon: 'i-lucide-braces'
  }
]

const formatDescriptions: Record<ExportFormat, string> = {
  pdf: 'Documento formatado, ideal para impressão e compartilhamento',
  csv: 'Planilha de dados, compatível com Excel e Google Sheets',
  json: 'Dados estruturados, ideal para análise técnica'
}

const handleExport = async () => {
  await exportData({
    format: selectedFormat.value,
    startDate: range.value.start,
    endDate: range.value.end,
    patientId: patientId.value,
    patientName: patientName.value
  })

  if (!isExporting.value) {
    if (isDoctor.value) {
      router.back()
    } else {
      router.push('/dashboard/main')
    }
  }
}

const handleCancel = () => {
  router.back()
}
</script>

<template>
  <UDashboardPanel>
    <template #header>
      <UDashboardNavbar title="Exportar Dados">
        <template #leading>
          <UButton icon="i-lucide-arrow-left" color="neutral" variant="ghost" @click="handleCancel" square />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-6 max-w-3xl mx-auto">
        <UCard>
          <template #header>
            <div class="flex items-center gap-3">
              <div class="p-2 bg-primary-50 dark:bg-primary-950 rounded-lg">
                <UIcon name="i-lucide-download" class="size-5 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <h3 class="text-lg font-semibold">Exportar Dados de Saúde</h3>
                <p class="text-sm text-muted">Selecione o formato e período desejado</p>
              </div>
            </div>
          </template>

          <div class="space-y-6">
            <div>
              <label class="block text-sm font-medium mb-3">Formato do arquivo</label>
              <div class="grid grid-cols-3 gap-3">
                <button v-for="format in formatTabs" :key="format.slot"
                  @click="selectedFormat = format.slot as ExportFormat" :class="[
                    'flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all',
                    selectedFormat === format.slot
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-950'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  ]">
                  <UIcon :name="format.icon" class="size-6" />
                  <span class="text-sm font-medium">{{ format.label }}</span>
                </button>
              </div>
              <p class="text-xs text-muted mt-2">
                {{ formatDescriptions[selectedFormat] }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium mb-3">Período</label>
              <DashboardHomeDateRangePicker v-model="range" />
              <p class="text-xs text-muted mt-2">
                Selecione o intervalo de datas que deseja exportar
              </p>
            </div>

            <UAlert color="info" variant="subtle" icon="i-lucide-info" title="Informações incluídas"
              description="O arquivo conterá: data de geração, nome completo do paciente, identificador único e todos os dados de saúde do período selecionado." />
          </div>

          <template #footer>
            <div class="flex justify-end gap-3">
              <UButton color="neutral" variant="ghost" @click="handleCancel" :disabled="isExporting">
                Cancelar
              </UButton>
              <UButton icon="i-lucide-download" @click="handleExport" :loading="isExporting" :disabled="isExporting">
                {{ isExporting ? 'Exportando...' : 'Exportar' }}
              </UButton>
            </div>
          </template>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>
</template>
