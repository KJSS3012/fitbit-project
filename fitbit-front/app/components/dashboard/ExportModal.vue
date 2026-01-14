<script setup lang="ts">
import { sub, startOfDay, endOfDay } from 'date-fns'
import type { Range } from '~/types/dashboard'
import type { ExportFormat } from '~/composables/useExport'
import type { TabsItem } from '@nuxt/ui/runtime/components/Tabs.vue.js'

interface Props {
  patientId: string
  initialRange?: Range
}

const props = defineProps<Props>()
const isOpen = defineModel<boolean>({ required: true })

const { exportData, isExporting } = useExport()

const selectedFormat = ref<ExportFormat>('pdf')
const range = ref<Range>(props.initialRange || {
  start: startOfDay(sub(new Date(), { days: 6 })),
  end: endOfDay(new Date())
})

const formatTabs: TabsItem[] = [
  {
    label: 'PDF',
    value: 'pdf',
    icon: 'i-lucide-file-text'
  },
  {
    label: 'CSV',
    value: 'csv',
    icon: 'i-lucide-table'
  },
  {
    label: 'JSON',
    value: 'json',
    icon: 'i-lucide-braces'
  }
]

const formatDescriptions = {
  pdf: 'Documento formatado, ideal para impressão e compartilhamento',
  csv: 'Planilha de dados, compatível com Excel e Google Sheets',
  json: 'Dados estruturados, ideal para análise técnica'
}

const handleExport = async () => {
  await exportData({
    format: selectedFormat.value,
    startDate: range.value.start,
    endDate: range.value.end,
    patientId: props.patientId
  })

  if (!isExporting.value) {
    isOpen.value = false
  }
}

watch(isOpen, (value) => {
  if (!value) {
    selectedFormat.value = 'pdf'
  }
})
</script>

<template>
  <UModal v-model="isOpen">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-primary-50 dark:bg-primary-950 rounded-lg">
              <UIcon name="i-lucide-download" class="size-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <h3 class="text-lg font-semibold">Exportar Dados</h3>
              <p class="text-sm text-muted">Selecione o formato e período desejado</p>
            </div>
          </div>
          <UButton icon="i-lucide-x" color="neutral" variant="ghost" square @click="isOpen = false"
            :disabled="isExporting" />
        </div>
      </template>

      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium mb-3">Formato do arquivo</label>
          <UTabs v-model="selectedFormat" :items="formatTabs" class="w-full" />
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
          <UButton color="neutral" variant="ghost" @click="isOpen = false" :disabled="isExporting">
            Cancelar
          </UButton>
          <UButton icon="i-lucide-download" @click="handleExport" :loading="isExporting" :disabled="isExporting">
            {{ isExporting ? 'Exportando...' : 'Exportar' }}
          </UButton>
        </div>
      </template>
    </UCard>
  </UModal>
</template>
