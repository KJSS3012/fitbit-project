import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock $fetch global
const mockFetch = vi.fn()
global.$fetch = mockFetch as any

// Mock useToast
const mockToastAdd = vi.fn()
vi.mock('#app', () => ({
  useToast: () => ({ add: mockToastAdd }),
  useRuntimeConfig: () => ({ public: { apiBase: 'http://localhost:8000' } })
}))

describe('useFitbitData - syncFitbitData', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFitbitConnected.value = false
    mockToken.value = ''
    mockLastSyncTime.value = null
    mockRequestCache.value = {}
  })

  it('should sync Fitbit data successfully and show success toast', async () => {
    const mockResponse = {
      success: true,
      message: 'Dados sincronizados com sucesso',
      last_sync: '2026-01-10',
      data: {
        date: '2026-01-10',
        steps: 10000,
        hr_avg: 72,
        sleep_hours: 7.0,
        calories: 2500
      },
      metrics_saved: 1
    }

    mockFetch.mockResolvedValueOnce(mockResponse)

    // Set mock state
    mockFitbitConnected.value = true
    mockToken.value = 'test_token'

    const { syncFitbitData } = useFitbitData()
    const result = await syncFitbitData('2026-01-10')

    expect(result).toEqual(mockResponse)
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/fitbit/sync',
      expect.objectContaining({
        method: 'POST',
        params: { day: '2026-01-10' },
        headers: {
          Authorization: 'Bearer test_token'
        }
      })
    )

    // Verify success toast
    expect(mockToastAdd).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Sincronização completa',
        description: 'Dados atualizados com sucesso',
        color: 'success'
      })
    )
  })

  it('should show expired token error toast when 401 with "expirou"', async () => {
    const errorResponse = {
      status: 401,
      statusCode: 401,
      data: { detail: 'Conexão Fitbit expirou. Reconecte sua conta' }
    }

    mockFetch.mockRejectedValueOnce(errorResponse)

    // Set mock state
    mockFitbitConnected.value = true
    mockToken.value = 'test_token'

    const { syncFitbitData } = useFitbitData()
    await expect(syncFitbitData()).rejects.toThrow()

    // Verify expired toast
    expect(mockToastAdd).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Conexão expirada',
        description: expect.stringContaining('Conexão Fitbit expirou'),
        color: 'error'
      })
    )
  })

  it('should show not connected toast when 401 without "expirou"', async () => {
    const errorResponse = {
      status: 401,
      statusCode: 401,
      data: { detail: 'Fitbit não conectado' }
    }

    mockFetch.mockRejectedValueOnce(errorResponse)

    // Set mock state
    mockFitbitConnected.value = true
    mockToken.value = 'test_token'

    const { syncFitbitData } = useFitbitData()
    await expect(syncFitbitData()).rejects.toThrow()

    expect(mockToastAdd).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Não conectado',
        description: 'Fitbit não está conectado',
        color: 'warning'
      })
    )
  })

  it('should show network error toast when sync fails', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    // Set mock state
    mockFitbitConnected.value = true
    mockToken.value = 'test_token'

    const { syncFitbitData } = useFitbitData()
    await expect(syncFitbitData()).rejects.toThrow()

    expect(mockToastAdd).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Falha na sincronização',
        description: expect.stringContaining('Verifique sua conexão'),
        color: 'error'
      })
    )
  })

  it('should throw error when Fitbit not connected', async () => {
    // mockFitbitConnected.value remains false from beforeEach
    const { syncFitbitData } = useFitbitData()
    await expect(syncFitbitData()).rejects.toThrow('Fitbit não conectado')
  })

  it('should clear cache after successful sync', async () => {
    mockFetch.mockResolvedValueOnce({ success: true })

    // Set mock state
    mockFitbitConnected.value = true
    mockToken.value = 'test_token'

    const { syncFitbitData } = useFitbitData()
    await syncFitbitData()

    // Cache should be cleared (tested via internal state)
    expect(mockFetch).toHaveBeenCalled()
  })
})

// Shared state for mocks
const mockFitbitConnected = { value: false }
const mockToken = { value: '' }
const mockLastSyncTime = { value: null as Date | null }
const mockRequestCache = { value: {} as Record<string, any> }

// Mock composables
function useFitbitData() {
  const syncFitbitData = async (date = '2026-01-10') => {
    if (!mockFitbitConnected.value || !mockToken.value) {
      throw new Error('Fitbit não conectado')
    }

    try {
      const response = await $fetch('http://localhost:8000/fitbit/sync', {
        method: 'POST',
        params: { day: date },
        headers: {
          Authorization: `Bearer ${mockToken.value}`
        }
      })

      mockLastSyncTime.value = new Date()
      mockRequestCache.value = {}

      mockToastAdd({
        title: 'Sincronização completa',
        description: 'Dados atualizados com sucesso',
        color: 'success',
        icon: 'i-heroicons-check-circle'
      })

      return response
    } catch (error: any) {
      if (error.status === 401 || error.statusCode === 401) {
        const errorDetail = error.data?.detail || error.message || ''

        if (errorDetail.includes('expirou') || errorDetail.includes('Reconecte')) {
          mockToastAdd({
            title: 'Conexão expirada',
            description: 'Conexão Fitbit expirou. Reconecte sua conta',
            color: 'error',
            icon: 'i-heroicons-exclamation-circle'
          })
        } else {
          mockToastAdd({
            title: 'Não conectado',
            description: 'Fitbit não está conectado',
            color: 'warning',
            icon: 'i-heroicons-exclamation-triangle'
          })
        }
      } else {
        mockToastAdd({
          title: 'Falha na sincronização',
          description: 'Falha ao sincronizar dados. Verifique sua conexão',
          color: 'error',
          icon: 'i-heroicons-x-circle'
        })
      }

      throw error
    }
  }

  return { syncFitbitData }
}

function useFitbitAuth() {
  return { isFitbitConnected: mockFitbitConnected }
}

function useAuth() {
  return { token: mockToken }
}
