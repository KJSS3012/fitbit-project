<template>
  <UModal>

    <!-- Floating Action Button for Notes -->
    <UButton icon="i-lucide-plus" color="primary" size="lg" class="fixed bottom-6 right-6 z-50 shadow-lg">
      Adicionar Nota
    </UButton>

    <template #content>
      <div class="p-6">
        <div class="flex items-center gap-3 mb-4">
          <UAvatar size="sm" color="primary">
            <UIcon name="i-lucide-sticky-note" class="size-5" />
          </UAvatar>
          <h3 class="text-lg font-semibold">Adicionar Anotação Clínica</h3>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <UFormField label="Tipo de Métrica (opcional)">
            <USelect v-model="form.metricType" :items="metricOptions" placeholder="Selecione o tipo" />
          </UFormField>

          <UFormField label="Período (opcional)">
            <div class="grid grid-cols-2 gap-2">
              <UInput v-model="form.startDate" type="date" placeholder="Data inicial" />
              <UInput v-model="form.endDate" type="date" placeholder="Data final" />
            </div>
          </UFormField>

          <UFormField label="Anotação" required>
            <UTextarea v-model="form.text" placeholder="Digite sua anotação clínica..." :rows=4 />
          </UFormField>

          <div class="flex gap-3 justify-end">
            <UButton variant="outline" @click="closeModal">
              Cancelar
            </UButton>
            <UButton type="submit" color="primary" :loading="loading">
              Salvar Anotação
            </UButton>
          </div>
        </form>
        
      </div>
    </template>

  </UModal>
</template>

<script setup lang="ts">
const props = defineProps<{
  patientCpf: string
}>()

const emit = defineEmits<{
  'update:isOpen': [value: boolean]
  'note-created': []
}>()

const toast = useToast()
const loading = ref(false)

const metricOptions = [
  { label: 'Frequência Cardíaca', value: 'hr' },
  { label: 'Passos', value: 'steps' },
  { label: 'Sono', value: 'sleep' }
]

const form = reactive({
  metricType: '',
  startDate: '',
  endDate: '',
  text: ''
})

const closeModal = () => {
  emit('update:isOpen', false)
  resetForm()
}

const resetForm = () => {
  form.metricType = ''
  form.startDate = ''
  form.endDate = ''
  form.text = ''
}

const handleSubmit = async () => {
  if (!form.text.trim()) {
    toast.add({
      title: 'Erro',
      description: 'A anotação não pode estar vazia',
      color: 'error'
    })
    return
  }

  loading.value = true

  try {
    const requestData: any = {
      patient_cpf: props.patientCpf,
      text: form.text.trim()
    }

    if (form.metricType) requestData.metric_type = form.metricType
    if (form.startDate) requestData.start_date = form.startDate
    if (form.endDate) requestData.end_date = form.endDate

    await $fetch('/notes/notes', {
      method: 'POST',
      body: requestData
    })

    toast.add({
      title: 'Sucesso',
      description: 'Anotação registrada com sucesso',
      color: 'success'
    })

    emit('note-created')
    closeModal()
  } catch (error: any) {
    toast.add({
      title: 'Erro',
      description: error?.data?.detail || 'Erro ao salvar anotação',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}
</script>