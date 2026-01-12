/**
 * Composable for doctor to manage and view authorized patients
 */
export const useDoctorPatients = () => {
  const config = useRuntimeConfig()
  const { token, user } = useAuth()
  const toast = useToast()

  const API_BASE_URL = config.public.apiBase || 'http://localhost:8000'

  const authorizedPatients = ref<any[]>([])
  const selectedPatientMetrics = ref<any>(null)
  const isLoading = ref(false)

  /**
   * Fetch list of patients authorized for current doctor
   */
  const fetchAuthorizedPatients = async () => {
    if (!token.value || !user.value) {
      throw new Error('Usuário não autenticado')
    }

    isLoading.value = true

    try {
      // For now, use mock data since we don't have /doctors/patients endpoint yet
      // TODO: Implement GET /doctors/{crm}/patients backend endpoint
      authorizedPatients.value = [
        {
          cpf: '52998224725',
          name: 'João da Silva',
          age: 45,
          status: 'active',
          lastSync: '2026-01-10T14:30:00'
        }
      ]

      return authorizedPatients.value
    } catch (error: any) {
      console.error('Error fetching patients:', error)
      toast.add({
        title: 'Erro ao carregar pacientes',
        description: 'Não foi possível buscar lista de pacientes autorizados',
        color: 'error',
        icon: 'i-heroicons-x-circle'
      })
      throw error
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch health metrics for specific patient
   * @param patientCpf - Patient CPF to query
   * @param startDate - Optional start date filter (YYYY-MM-DD)
   * @param endDate - Optional end date filter (YYYY-MM-DD)
   */
  const fetchPatientMetrics = async (
    patientCpf: string,
    startDate?: string,
    endDate?: string
  ) => {
    if (!token.value || !user.value) {
      throw new Error('Usuário não autenticado')
    }

    const doctorCrm = user.value.id // CRM from JWT

    isLoading.value = true

    try {
      const params: any = { doctor_crm: doctorCrm }
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate

      const response = await $fetch(
        `${API_BASE_URL}/users/patients/${patientCpf}/health-metrics`,
        {
          params,
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        }
      )

      selectedPatientMetrics.value = response
      return response
    } catch (error: any) {
      console.error('Error fetching patient metrics:', error)

      // Handle 403 - Not authorized
      if (error?.response?.status === 403 || error?.status === 403) {
        const detail = error?.data?.detail || error?.response?.data?.detail || ''

        if (detail.includes('não autorizou')) {
          toast.add({
            title: 'Acesso negado',
            description: 'Paciente não autorizou compartilhamento de dados',
            color: 'warning',
            icon: 'i-heroicons-exclamation-triangle'
          })
          throw new Error('Paciente não autorizou compartilhamento de dados')
        }

        toast.add({
          title: 'Acesso negado',
          description: detail || 'Você não tem permissão para acessar esses dados',
          color: 'error',
          icon: 'i-heroicons-shield-exclamation'
        })
        throw new Error(detail)
      }

      // Handle 404 - Patient not found
      if (error?.response?.status === 404 || error?.status === 404) {
        toast.add({
          title: 'Paciente não encontrado',
          description: 'CPF não encontrado no sistema',
          color: 'error',
          icon: 'i-heroicons-user-minus'
        })
        throw new Error('Paciente não encontrado')
      }

      // Generic error
      toast.add({
        title: 'Erro ao carregar métricas',
        description: 'Não foi possível buscar dados do paciente',
        color: 'error',
        icon: 'i-heroicons-x-circle'
      })
      throw error
    } finally {
      isLoading.value = false
    }
  }

  return {
    authorizedPatients,
    selectedPatientMetrics,
    isLoading,
    fetchAuthorizedPatients,
    fetchPatientMetrics
  }
}
