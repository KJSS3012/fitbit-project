<script setup lang="ts">
import type { DropdownMenuItem } from '@nuxt/ui'
import type { ClinicalNote } from '~/composables/useNotes'
import NoteModal from '~/components/shared/NoteModal.vue'


interface Props {
  patientCpf: string
  reloadTrigger?: number
  readOnly?: boolean
}

const props = defineProps<Props>()

const { fetchNotes, deleteNote } = useNotes()
const toast = useToast()


const notes = ref<ClinicalNote[]>([])
const isLoading = ref(false)
const isDrawerOpen = ref(false)

// Reload notes when reloadTrigger changes
watch(() => props.reloadTrigger, async (newVal, oldVal) => {
  if (newVal !== oldVal && isDrawerOpen.value) {
    await loadNotes()
  }
})


const overlay = useOverlay()
const modal = overlay.create(NoteModal);



async function loadNotes() {
  isLoading.value = true
  try {
    notes.value = await fetchNotes(props.patientCpf)
  } catch (error: any) {
    toast.add({
      title: 'Erro ao carregar notas',
      description: error.message || 'Não foi possível carregar as notas médicas',
      color: 'error'
    })
  } finally {
    isLoading.value = false
  }
}

async function handleDeleteNote(noteId: string) {
  try {
    await deleteNote(noteId)
    notes.value = notes.value.filter(note => note.id !== noteId)
    toast.add({
      title: 'Nota excluída',
      description: 'A nota médica foi excluída com sucesso',
      color: 'success'
    })
  } catch (error: any) {
    toast.add({
      title: 'Erro ao excluir nota',
      description: error.message || 'Não foi possível excluir a nota médica',
      color: 'error'
    })
  }
}

function getDropdownActions(noteId: string): DropdownMenuItem[] {
  return [
    {
      label: 'Delete',
      icon: 'i-lucide-trash-2',
      value: 'delete',
      color: 'error',
      onSelect() {
        handleDeleteNote(noteId)
      }
    }
  ]
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}
</script>

<template>
  <UDrawer v-model="isDrawerOpen" title="Notas Médicas" description="Visualize todas as anotações médicas do paciente"
    direction="right" :overlay="false" :handle="false">
    <UButton icon="i-lucide-eye" class="fixed bottom-6 right-6 z-50 shadow-lg" color="primary" size="lg"
      @click="loadNotes()">
      Visualizar Notas
    </UButton>
    <template #body>
      <div class="space-y-4">
        <!-- Add Note Button - Only show if not read-only -->
        <div v-if="!props.readOnly" class="flex justify-end">
          <UButton @click="modal.open({ patientCpf: props.patientCpf }).then((data) => { data ? loadNotes() : null })"
            icon="i-lucide-plus" color="primary">
            Adicionar Nota
          </UButton>
        </div>
        <!-- Loading Skeleton -->
        <template v-if="isLoading">
          <UCard v-for="i in 3" :key="i" variant="outline">
            <UCardSection class="flex justify-between mb-4">
              <div class="flex items-center gap-2">
                <USkeleton class="w-10 h-10 rounded-full" />
                <div class="space-y-2">
                  <USkeleton class="h-4 w-24" />
                  <USkeleton class="h-3 w-20" />
                </div>
              </div>
              <USkeleton class="w-8 h-8 rounded" />
            </UCardSection>
            <USkeleton class="h-20 w-full" />
          </UCard>
        </template>

        <!-- Empty State -->
        <template v-else-if="notes.length === 0">
          <UCard variant="outline">
            <div class="text-center py-8 text-gray-500">
              <UIcon name="i-lucide-file-text" class="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Nenhuma nota médica encontrada</p>
            </div>
          </UCard>
        </template>

        <!-- Notes List -->
        <template v-else>
          <UCard v-for="note in notes" :key="note.id" variant="outline">
            <UCardSection class="flex justify-between mb-4">
              <div class="flex items-center gap-2">
                <UAvatar icon="i-lucide-user" />
                <div>
                  <div class="text-sm font-medium">Dr. {{ note.doctor_crm }}</div>
                  <div class="text-xs text-gray-500">{{ formatDate(note.created_at) }}</div>
                </div>
              </div>

              <UDropdownMenu v-if="!props.readOnly" :items="getDropdownActions(note.id)" :ui="{ content: 'w-48' }">
                <UButton icon="i-lucide-more-vertical" color="neutral" variant="ghost" size="sm" />
              </UDropdownMenu>
            </UCardSection>

            <div class="text-sm whitespace-pre-wrap">{{ note.text }}</div>

            <!-- Optional metadata -->
            <div v-if="note.metric_type || note.start_date"
              class="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
              <span v-if="note.metric_type" class="mr-3">
                <UIcon name="i-lucide-activity" class="inline" />
                {{ note.metric_type }}
              </span>
              <span v-if="note.start_date">
                <UIcon name="i-lucide-calendar" class="inline" />
                {{ formatDate(note.start_date) }}
                <template v-if="note.end_date"> - {{ formatDate(note.end_date) }}</template>
              </span>
            </div>
          </UCard>
        </template>
      </div>
    </template>
  </UDrawer>
</template>

<style scoped></style>