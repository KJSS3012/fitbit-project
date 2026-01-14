<template>
  <UModal>
    <!-- Floating Action Button for Notes - Only show if not controlled externally -->

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
            <USelect v-model="form.metricType" :items="metricOptions" placeholder="Selecione o tipo"
              :disabled="isSubmitting" />
          </UFormField>

          <UFormField label="Período (opcional)">
            <div class="grid grid-cols-2 gap-2">
              <UInput v-model="form.startDate" type="date" placeholder="Data inicial" :disabled="isSubmitting" />
              <UInput v-model="form.endDate" type="date" placeholder="Data final" :disabled="isSubmitting"
                :min="form.startDate" />
            </div>
            <p v-if="dateError" class="text-xs text-red-500 mt-1">
              {{ dateError }}
            </p>
          </UFormField>

          <UFormField label="Anotação" required>
            <UTextarea v-model="form.text" placeholder="Digite sua anotação clínica..." :rows="6"
              :disabled="isSubmitting" :maxlength="244" class="w-full"/>
            <div class="mt-1 w-full">
              <p v-if="textError" class="text-xs text-red-500">
                {{ textError }}
              </p>
              <p class="text-xs text-gray-500 ml-auto">
                {{ form.text.length }}/244
              </p>
            </div>
          </UFormField>

          <div class="flex gap-3 justify-end">
            <UButton variant="outline" @click="closeModal" :disabled="isSubmitting">
              Cancelar
            </UButton>
            <UButton type="submit" color="primary" :loading="isSubmitting" :disabled="!isFormValid">
              Salvar Anotação
            </UButton>
          </div>
        </form>
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { CreateNoteData } from '~/composables/useNotes'

const props = defineProps<{
  patientCpf: string
  modelValue?: boolean
}>()

const emit = defineEmits<{
  'note-created': []
  'update:modelValue': [value: boolean]
  'close': [boolean]
}>()

const { createNote } = useNotes()
const toast = useToast()


const isSubmitting = ref(false)
const textError = ref('')
const dateError = ref('')

const metricOptions = [
  { label: 'Frequência Cardíaca', value: 'hr' },
  { label: 'Passos', value: 'steps' },
  { label: 'Sono', value: 'sleep' },
  { label: 'Atividade', value: 'activity' },
  { label: 'Calorias', value: 'calories' }
]

const form = reactive({
  metricType: '',
  startDate: '',
  endDate: '',
  text: ''
})

const isFormValid = computed(() => {
  return form.text.trim().length > 0 &&
    form.text.length <= 244 &&
    !dateError.value
})

// Validate dates
watch([() => form.startDate, () => form.endDate], () => {
  dateError.value = ''

  if (form.startDate && form.endDate) {
    const start = new Date(form.startDate)
    const end = new Date(form.endDate)

    if (end < start) {
      dateError.value = 'A data final deve ser posterior à data inicial'
    }
  }
})

// Validate text
watch(() => form.text, () => {
  textError.value = ''

  if (form.text.length > 244) {
    textError.value = 'A anotação não pode exceder 244 caracteres'
  }
})


const closeModal = () => {
  if (isSubmitting.value) return

  // Confirm if there's unsaved content
  if (form.text.trim().length > 0) {
    const confirmed = confirm('Tem certeza que deseja cancelar? As alterações não salvas serão perdidas.')
    if (!confirmed) return
  }

  emit('close')
  resetForm()
}

const resetForm = () => {
  form.metricType = ''
  form.startDate = ''
  form.endDate = ''
  form.text = ''
  textError.value = ''
  dateError.value = ''
}

const handleSubmit = async () => {
  // Client-side validation
  if (!form.text.trim()) {
    textError.value = 'A anotação não pode estar vazia'
    toast.add({
      title: 'Erro de Validação',
      description: 'Por favor, preencha a anotação',
      color: 'error'
    })
    return
  }

  if (form.text.length > 244) {
    textError.value = 'A anotação não pode exceder 244 caracteres'
    return
  }

  if (dateError.value) {
    toast.add({
      title: 'Erro de Validação',
      description: dateError.value,
      color: 'error'
    })
    return
  }

  isSubmitting.value = true

  try {
    const noteData: CreateNoteData = {
      patient_cpf: props.patientCpf,
      text: form.text.trim()
    }

    // Only add optional fields if they have values
    if (form.metricType) {
      noteData.metric_type = form.metricType
    }
    if (form.startDate) {
      noteData.start_date = form.startDate
    }
    if (form.endDate) {
      noteData.end_date = form.endDate
    }

    await createNote(noteData)

    toast.add({
      title: 'Sucesso',
      description: 'Anotação clínica registrada com sucesso',
      color: 'success',
      icon: 'i-lucide-check-circle'
    })

    emit('note-created')
    emit('close', { sendedData: true })
    resetForm()
  } catch (error: any) {
    console.error('Error creating note:', error)

    const errorMessage = error?.data?.detail ||
      error?.message ||
      'Não foi possível salvar a anotação. Tente novamente.'

    toast.add({
      title: 'Erro ao Salvar',
      description: errorMessage,
      color: 'error',
      icon: 'i-lucide-alert-circle'
    })
  } finally {
    isSubmitting.value = false
  }
}

// Close modal when pressing Escape (if not submitting)
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && !isSubmitting.value) {
    closeModal()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* Optional: Add smooth transitions */
.v-enter-active,
.v-leave-active {
  transition: opacity 0.2s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>