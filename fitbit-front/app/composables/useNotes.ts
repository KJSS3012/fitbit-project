export interface ClinicalNote {
  id: string
  patient_cpf: string
  doctor_crm: string
  doctor_name: string
  text: string
  metric_type?: string | null
  start_date?: string | null
  end_date?: string | null
  created_at: string
}

export interface CreateNoteData {
  patient_cpf: string
  text: string
  metric_type?: string
  start_date?: string
  end_date?: string
}

export const useNotes = () => {
  const config = useRuntimeConfig()
  const token = useCookie('auth_token')
  const API_BASE_URL = config.public.apiBase

  const fetchNotes = async (cpf: string): Promise<ClinicalNote[]> => {
    const response = await $fetch<ClinicalNote[]>(`${API_BASE_URL}/notes/${cpf}`, {
      headers: {
        Authorization: `Bearer ${token.value}`
      }
    })
    return response
  }

  const createNote = async (data: CreateNoteData) => {
    const response = await $fetch(`${API_BASE_URL}/notes`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token.value}`,
        'Content-Type': 'application/json'
      },
      body: data
    })
    return response
  }

  const deleteNote = async (noteId: string) => {
    // Assuming there's a delete endpoint
    const response = await $fetch(`${API_BASE_URL}/notes/${noteId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token.value}`
      }
    })
    return response
  }

  return {
    fetchNotes,
    createNote,
    deleteNote
  }
}