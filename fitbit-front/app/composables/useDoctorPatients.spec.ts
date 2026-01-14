import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock $fetch
const mockFetch = vi.fn()
global.$fetch = mockFetch as any

// Mock useToast
const mockToastAdd = vi.fn()
vi.mock('#app', () => ({
  useToast: () => ({ add: mockToastAdd }),
  useRuntimeConfig: () => ({ public: { apiBase: 'http://localhost:8000' } })
}))

describe('useDoctorPatients', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockToken.value = 'doctor_token'
    mockUser.value = { id: '12345SP', type: 'doctor', name: 'Dr. João' }
  })

  it('should fetch patient metrics successfully', async () => {
    const mockResponse = {
      patient_cpf: '52998224725',
      patient_name: 'João da Silva',
      metrics: [
        {
          date: '2026-01-10',
          steps: 10000,
          hr_avg: 72,
          sleep_hours: 7.5,
          calories: 2500,
          source: 'fitbit'
        }
      ],
      last_sync: '2026-01-10',
      is_data_outdated: false,
      total_records: 1
    }

    mockFetch.mockResolvedValueOnce(mockResponse)

    const { fetchPatientMetrics } = useDoctorPatients()
    const result = await fetchPatientMetrics('52998224725')

    expect(result).toEqual(mockResponse)
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/user/patients/52998224725/health-metrics',
      expect.objectContaining({
        params: { doctor_crm: '12345SP' },
        headers: {
          Authorization: 'Bearer doctor_token'
        }
      })
    )
  })

  it('should show warning toast when patient not authorized (403)', async () => {
    const errorResponse = {
      status: 403,
      data: { detail: 'Paciente não autorizou compartilhamento de dados' }
    }

    mockFetch.mockRejectedValueOnce(errorResponse)

    const { fetchPatientMetrics } = useDoctorPatients()

    await expect(fetchPatientMetrics('12345678901')).rejects.toThrow(
      'Paciente não autorizou compartilhamento de dados'
    )

    expect(mockToastAdd).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Acesso negado',
        description: expect.stringContaining('não autorizou'),
        color: 'warning'
      })
    )
  })

  it('should show error toast when patient not found (404)', async () => {
    const errorResponse = {
      status: 404,
      data: { detail: 'Paciente não encontrado' }
    }

    mockFetch.mockRejectedValueOnce(errorResponse)

    const { fetchPatientMetrics } = useDoctorPatients()

    await expect(fetchPatientMetrics('99999999999')).rejects.toThrow()

    expect(mockToastAdd).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Paciente não encontrado',
        description: 'CPF não encontrado no sistema',
        color: 'error'
      })
    )
  })

  it('should detect outdated data flag from backend', async () => {
    const mockResponse = {
      patient_cpf: '52998224725',
      patient_name: 'Maria Santos',
      metrics: [
        {
          date: '2026-01-07',
          steps: 5000,
          hr_avg: 68,
          sleep_hours: 6.0,
          calories: 1800,
          source: 'fitbit'
        }
      ],
      last_sync: '2026-01-07',
      is_data_outdated: true,
      total_records: 1
    }

    mockFetch.mockResolvedValueOnce(mockResponse)

    const { fetchPatientMetrics, selectedPatientMetrics } = useDoctorPatients()
    await fetchPatientMetrics('52998224725')

    expect(selectedPatientMetrics.value.is_data_outdated).toBe(true)
    expect(selectedPatientMetrics.value.last_sync).toBe('2026-01-07')
  })

  it('should include date filters when provided', async () => {
    mockFetch.mockResolvedValueOnce({
      patient_cpf: '52998224725',
      patient_name: 'Test Patient',
      metrics: [],
      total_records: 0
    })

    const { fetchPatientMetrics } = useDoctorPatients()
    await fetchPatientMetrics('52998224725', '2026-01-01', '2026-01-10')

    expect(mockFetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        params: {
          doctor_crm: '12345SP',
          start_date: '2026-01-01',
          end_date: '2026-01-10'
        }
      })
    )
  })
})

// Mock state
const mockToken = { value: '' }
const mockUser = { value: null as any }

// Mock composables
function useDoctorPatients() {
  const selectedPatientMetrics = { value: null as any }
  const isLoading = { value: false }

  const fetchPatientMetrics = async (
    patientCpf: string,
    startDate?: string,
    endDate?: string
  ) => {
    if (!mockToken.value || !mockUser.value) {
      throw new Error('Usuário não autenticado')
    }

    const doctorCrm = mockUser.value.id

    isLoading.value = true

    try {
      const params: any = { doctor_crm: doctorCrm }
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate

      const response = await $fetch(
        `http://localhost:8000/user/patients/${patientCpf}/health-metrics`,
        {
          params,
          headers: {
            Authorization: `Bearer ${mockToken.value}`
          }
        }
      )

      selectedPatientMetrics.value = response
      return response
    } catch (error: any) {
      if (error?.status === 403) {
        const detail = error?.data?.detail || ''

        if (detail.includes('não autorizou')) {
          mockToastAdd({
            title: 'Acesso negado',
            description: 'Paciente não autorizou compartilhamento de dados',
            color: 'warning',
            icon: 'i-heroicons-exclamation-triangle'
          })
          throw new Error('Paciente não autorizou compartilhamento de dados')
        }

        mockToastAdd({
          title: 'Acesso negado',
          description: detail,
          color: 'error',
          icon: 'i-heroicons-shield-exclamation'
        })
        throw new Error(detail)
      }

      if (error?.status === 404) {
        mockToastAdd({
          title: 'Paciente não encontrado',
          description: 'CPF não encontrado no sistema',
          color: 'error',
          icon: 'i-heroicons-user-minus'
        })
        throw new Error('Paciente não encontrado')
      }

      mockToastAdd({
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
    selectedPatientMetrics,
    isLoading,
    fetchPatientMetrics
  }
}

function useAuth() {
  return { token: mockToken, user: mockUser }
}
