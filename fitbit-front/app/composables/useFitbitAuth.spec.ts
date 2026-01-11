/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mocks simplificados
const mockToast = { add: vi.fn() }
const mockToken = { value: 'test-token-123' }
const mockRoute = { query: {} }
const mockRouter = { replace: vi.fn() }
const mockConfig = { public: { apiBase: 'http://localhost:8000' } }
const mockFitbitConnected = { value: false }
const mockFitbitConnecting = { value: false }

// Mock dos composables do Nuxt
vi.stubGlobal('useToast', () => mockToast)
vi.stubGlobal('useRoute', () => mockRoute)
vi.stubGlobal('useRouter', () => mockRouter)
vi.stubGlobal('useRuntimeConfig', () => mockConfig)
vi.stubGlobal('useAuth', () => ({ token: mockToken }))
vi.stubGlobal('useState', (key: string) => {
  if (key === 'fitbitConnected') return mockFitbitConnected
  if (key === 'fitbitConnecting') return mockFitbitConnecting
  return { value: null }
})

  ; (global as any).$fetch = vi.fn()

import { useFitbitAuth } from './useFitbitAuth'

describe('useFitbitAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRoute.query = {}
    mockToken.value = 'test-token-123'
    mockFitbitConnected.value = false
    mockFitbitConnecting.value = false
  })

  it('deve inicializar com valores padrão', () => {
    const { isFitbitConnected, isConnecting } = useFitbitAuth()

    expect(isFitbitConnected.value).toBe(false)
    expect(isConnecting.value).toBe(false)
  })

  it('deve mostrar toast ao conectar', () => {
    const { connectFitbit } = useFitbitAuth()

    connectFitbit()

    expect(mockToast.add).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Redirecionando para Fitbit',
        color: 'info'
      })
    )
    expect(mockFitbitConnecting.value).toBe(true)
  })

  it('deve detectar conexão via query param', async () => {
    mockRoute.query = { fitbit: 'connected' }
    const { checkFitbitStatus } = useFitbitAuth()

    await checkFitbitStatus()

    expect(mockFitbitConnected.value).toBe(true)
    expect(mockRouter.replace).toHaveBeenCalledWith({ query: {} })
    expect(mockToast.add).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Fitbit conectado com sucesso!',
        color: 'success'
      })
    )
  })

  it('deve detectar negação do usuário via query param', async () => {
    mockRoute.query = { fitbit: 'denied' }
    const { checkFitbitStatus } = useFitbitAuth()

    await checkFitbitStatus()

    expect(mockFitbitConnected.value).toBe(false)
    expect(mockFitbitConnecting.value).toBe(false)
    expect(mockRouter.replace).toHaveBeenCalledWith({ query: {} })
    expect(mockToast.add).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Conexão cancelada pelo usuário',
        color: 'warning'
      })
    )
  })

  it('deve detectar erro de servidor via query param', async () => {
    mockRoute.query = { fitbit: 'error' }
    const { checkFitbitStatus } = useFitbitAuth()

    await checkFitbitStatus()

    expect(mockFitbitConnected.value).toBe(false)
    expect(mockFitbitConnecting.value).toBe(false)
    expect(mockRouter.replace).toHaveBeenCalledWith({ query: {} })
    expect(mockToast.add).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Erro ao finalizar conexão',
        color: 'error'
      })
    )
  })

  it('deve buscar status da API quando há token', async () => {
    ; (global.$fetch as any).mockResolvedValue({ connected: true })
    const { checkFitbitStatus } = useFitbitAuth()

    await checkFitbitStatus()

    expect(global.$fetch).toHaveBeenCalledWith(
      'http://localhost:8000/fitbit/status',
      expect.objectContaining({
        headers: { Authorization: 'Bearer test-token-123' }
      })
    )
    expect(mockFitbitConnected.value).toBe(true)
  })

  it('deve tratar erro ao verificar status', async () => {
    ; (global.$fetch as any).mockRejectedValue(new Error('Network error'))
    const { checkFitbitStatus } = useFitbitAuth()

    await checkFitbitStatus()

    expect(mockFitbitConnected.value).toBe(false)
  })

  it('deve desconectar Fitbit com sucesso', async () => {
    ; (global.$fetch as any).mockResolvedValue({})
    const { disconnectFitbit } = useFitbitAuth()
    mockFitbitConnected.value = true

    await disconnectFitbit()

    expect(global.$fetch).toHaveBeenCalledWith(
      'http://localhost:8000/fitbit/disconnect',
      expect.objectContaining({ method: 'POST' })
    )
    expect(mockFitbitConnected.value).toBe(false)
  })

  it('deve mostrar erro ao falhar desconexão', async () => {
    ; (global.$fetch as any).mockRejectedValue(new Error('API error'))
    const { disconnectFitbit } = useFitbitAuth()

    await disconnectFitbit()

    expect(mockToast.add).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Erro ao desconectar',
        color: 'error'
      })
    )
  })
})
