/**
 * Composable for managing doctor-patient data sharing authorizations.
 * PB11: Patient controls which doctors can access their health data.
 */
export const useAuthorization = () => {
  const config = useRuntimeConfig()
  const { token, user } = useAuth()
  const toast = useToast()

  const API_BASE_URL = config.public.apiBase || 'http://localhost:8000'

  const authorizedDoctors = ref<any[]>([])
  const isLoading = ref(false)

  /**
   * Fetch list of doctors with authorization status for current patient.
   * PB11 Scenario 4: Returns empty array if no doctors linked.
   */
  const fetchAuthorizedDoctors = async () => {
    if (!token.value || !user.value) {
      throw new Error('Usuário não autenticado')
    }

    if (user.value.type !== 'paciente') {
      throw new Error('Apenas pacientes podem visualizar autorizações')
    }

    isLoading.value = true

    try {
      const response = await $fetch<any[]>(
        `${API_BASE_URL}/auth/doctors`,
        {
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        }
      )

      authorizedDoctors.value = response
      return response
    } catch (error: any) {
      console.error('Error fetching authorized doctors:', error)

      toast.add({
        title: 'Erro ao carregar médicos',
        description: 'Não foi possível buscar lista de médicos autorizados',
        color: 'error',
        icon: 'i-heroicons-x-circle'
      })
      throw error
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Toggle doctor's authorization to access patient data.
   * PB11 Scenario 1: Grant authorization → "Compartilhamento ativado"
   * PB11 Scenario 2: Revoke authorization → "Revogado"
   * PB11 Scenario 3: Audit error → Error toast
   */
  const toggleDoctorAuthorization = async (doctorCrm: string, doctorName: string) => {
    if (!token.value || !user.value) {
      throw new Error('Usuário não autenticado')
    }

    isLoading.value = true

    try {
      const response = await $fetch<any>(
        `${API_BASE_URL}/auth/doctors/${doctorCrm}`,
        {
          method: 'PATCH',
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        }
      )

      // Update local state
      const doctor = authorizedDoctors.value.find(d => d.crm === doctorCrm)
      if (doctor) {
        doctor.authorized = response.authorized
      }

      // Show success toast
      if (response.authorized) {
        toast.add({
          title: 'Compartilhamento ativado',
          description: `Dr. ${doctorName} agora pode visualizar seus dados`,
          color: 'success',
          icon: 'i-heroicons-check-circle'
        })
      } else {
        toast.add({
          title: 'Compartilhamento revogado',
          description: `Dr. ${doctorName} não pode mais visualizar seus dados`,
          color: 'warning',
          icon: 'i-heroicons-shield-exclamation'
        })
      }

      return response
    } catch (error: any) {
      console.error('Error toggling authorization:', error)

      // PB11 Scenario 3: Audit error
      if (error?.data?.detail?.includes('auditoria')) {
        toast.add({
          title: 'Erro ao registrar auditoria',
          description: 'Operação não concluída. Tente novamente.',
          color: 'error',
          icon: 'i-heroicons-exclamation-triangle'
        })
      } else {
        toast.add({
          title: 'Erro ao alterar autorização',
          description: error?.data?.detail || 'Não foi possível alterar autorização',
          color: 'error',
          icon: 'i-heroicons-x-circle'
        })
      }
      throw error
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Add new doctor authorization by CRM.
   */
  const addDoctorAuthorization = async (doctorCrm: string) => {
    if (!token.value || !user.value) {
      throw new Error('Usuário não autenticado')
    }

    isLoading.value = true

    try {
      const response = await $fetch<any>(
        `${API_BASE_URL}/auth/doctors`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token.value}`
          },
          body: {
            doctor_crm: doctorCrm
          }
        }
      )

      // Refresh list
      await fetchAuthorizedDoctors()

      toast.add({
        title: 'Médico adicionado',
        description: response.message,
        color: 'success',
        icon: 'i-heroicons-user-plus'
      })

      return response
    } catch (error: any) {
      console.error('Error adding doctor:', error)

      if (error?.status === 404 || error?.response?.status === 404) {
        toast.add({
          title: 'Médico não encontrado',
          description: 'CRM não cadastrado no sistema',
          color: 'error',
          icon: 'i-heroicons-user-minus'
        })
      } else if (error?.status === 400 || error?.response?.status === 400) {
        toast.add({
          title: 'Médico já vinculado',
          description: error?.data?.detail || 'Este médico já está na sua lista',
          color: 'warning',
          icon: 'i-heroicons-exclamation-circle'
        })
      } else {
        toast.add({
          title: 'Erro ao adicionar médico',
          description: 'Não foi possível adicionar o médico',
          color: 'error',
          icon: 'i-heroicons-x-circle'
        })
      }
      throw error
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Revoke all doctor authorizations for the current patient.
   */
  const revokeAllAuthorizations = async () => {
    if (!token.value || !user.value) {
      throw new Error('Usuário não autenticado')
    }

    try {
      const response = await $fetch<any>(
        `${API_BASE_URL}/auth/doctors/all`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        }
      )

      // Refresh the list after revoking all
      await fetchAuthorizedDoctors()

      toast.add({
        title: 'Autorizações revogadas',
        description: response.message,
        color: 'success',
        icon: 'i-heroicons-check-circle'
      })

      return response
    } catch (error: any) {
      console.error('Error revoking all authorizations:', error)

      toast.add({
        title: 'Erro ao revogar autorizações',
        description: error?.data?.detail || 'Ocorreu um erro inesperado.',
        color: 'error',
        icon: 'i-heroicons-exclamation-triangle'
      })
      throw error
    }
  }

  /**
   * Set data type for doctor's authorization (Fitbit or Simulation).
   */
  const setDoctorDataType = async (doctorCrm: string, dataType: string) => {
    if (!token.value || !user.value) {
      throw new Error('Usuário não autenticado')
    }

    isLoading.value = true

    try {
      const response = await $fetch<any>(
        `${API_BASE_URL}/auth/doctors/${doctorCrm}`,
        {
          method: 'PATCH',
          headers: {
            Authorization: `Bearer ${token.value}`
          },
          body: {
            data_type: dataType
          }
        }
      )

      // Update local state
      const doctor = authorizedDoctors.value.find(d => d.crm === doctorCrm)
      if (doctor) {
        doctor.data_type = response.data_type
      }

      toast.add({
        title: 'Tipo de dados atualizado',
        description: `Tipo de dados alterado para ${dataType === 'fitbit' ? 'Fitbit' : 'Simulação'}`,
        color: 'success',
        icon: 'i-heroicons-check-circle'
      })

      return response
    } catch (error: any) {
      console.error('Error setting data type:', error)

      toast.add({
        title: 'Erro ao alterar tipo de dados',
        description: error?.data?.detail || 'Não foi possível alterar o tipo de dados',
        color: 'error',
        icon: 'i-heroicons-x-circle'
      })
      throw error
    } finally {
      isLoading.value = false
    }
  }

  return {
    authorizedDoctors,
    isLoading,
    fetchAuthorizedDoctors,
    toggleDoctorAuthorization,
    addDoctorAuthorization,
    revokeAllAuthorizations,
    setDoctorDataType
  }
}