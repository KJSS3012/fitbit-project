/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useFitbitAuth } from './useFitbitAuth'

// Mock composables
const mockToast = { add: vi.fn() }
const mockToken = { value: 'test-token-123' as string | null }
const mockRoute = { query: {} }
const mockRouter = { replace: vi.fn() }
const mockConfig = { public: { apiBaseUrl: 'http://localhost:8000' } }

vi.mock('#app', () => ({
  useToast: () => mockToast,
  useRoute: () => mockRoute,
  useRouter: () => mockRouter,
  useRuntimeConfig: () => mockConfig,
  useState: (key: string, init?: () => any) => {
    const states: Record<string, any> = {
      'fitbit-connected': { value: false },
      'fitbit-connecting': { value: false }
    }
    if (states[key]) {
      return states[key]
    }
    return { value: init ? init() : null }
  }
}))

vi.mock('./useAuth', () => ({
  useAuth: () => ({ token: mockToken })
}))

  ; (global as any).$fetch = vi.fn()

describe('useFitbitAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRoute.query = {}
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('connectFitbit', () => {
    it('deve redirecionar para OAuth do Fitbit', () => {
      const { connectFitbit } = useFitbitAuth()

      // Mock window.location
      delete (window as any).location
      window.location = { href: '' } as any

      connectFitbit()

      expect(mockToast.add).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Conectando com Fitbit...',
          color: 'neutral'
        })
      )
      expect(window.location.href).toBe('http://localhost:8000/fitbit/auth')
    })
  })

  describe('checkFitbitStatus', () => {
    it('deve detectar query param fitbit=connected', async () => {
      mockRoute.query = { fitbit: 'connected' }
      const { checkFitbitStatus, isFitbitConnected } = useFitbitAuth()

      await checkFitbitStatus()

      expect(isFitbitConnected.value).toBe(true)
      expect(mockToast.add).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Fitbit conectado com sucesso!',
          color: 'success'
        })
      )
      expect(mockRouter.replace).toHaveBeenCalledWith({ query: {} })
    })

    it('deve chamar API /fitbit/status quando há token', async () => {
      const mockResponse = { connected: true, hasData: true }
        ; (global.$fetch as any).mockResolvedValue(mockResponse)

      const { checkFitbitStatus, isFitbitConnected } = useFitbitAuth()

      await checkFitbitStatus()

      expect(global.$fetch).toHaveBeenCalledWith(
        'http://localhost:8000/fitbit/status',
        expect.objectContaining({
          headers: { Authorization: 'Bearer test-token-123' }
        })
      )
      expect(isFitbitConnected.value).toBe(true)
    })

    it('deve tratar erro da API gracefully', async () => {
      ; (global.$fetch as any).mockRejectedValue(new Error('Network error'))

      const { checkFitbitStatus, isFitbitConnected } = useFitbitAuth()

      await checkFitbitStatus()

      expect(isFitbitConnected.value).toBe(false)
    })

    it('não deve chamar API se não houver token', async () => {
      mockToken.value = null

      const { checkFitbitStatus } = useFitbitAuth()

      await checkFitbitStatus()

      expect(global.$fetch).not.toHaveBeenCalled()
    })
  })

  describe('disconnectFitbit', () => {
    it('deve chamar POST /fitbit/disconnect', async () => {
      ; (global.$fetch as any).mockResolvedValue({ success: true })

      const { disconnectFitbit, isFitbitConnected } = useFitbitAuth()
      isFitbitConnected.value = true

      await disconnectFitbit()

      expect(global.$fetch).toHaveBeenCalledWith(
        'http://localhost:8000/fitbit/disconnect',
        expect.objectContaining({
          method: 'POST',
          headers: { Authorization: 'Bearer test-token-123' }
        })
      )
      expect(isFitbitConnected.value).toBe(false)
      expect(mockToast.add).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Fitbit desconectado',
          color: 'neutral'
        })
      )
    })

    it('deve mostrar erro se desconexão falhar', async () => {
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

    it('deve falhar se não houver token', async () => {
      mockToken.value = null

      const { disconnectFitbit } = useFitbitAuth()

      await disconnectFitbit()

      expect(global.$fetch).not.toHaveBeenCalled()
      expect(mockToast.add).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Erro ao desconectar'
        })
      )
    })
  })

  describe('Estados', () => {
    it('deve inicializar com valores padrão', () => {
      const { isFitbitConnected, isConnecting } = useFitbitAuth()

      expect(isFitbitConnected.value).toBe(false)
      expect(isConnecting.value).toBe(false)
    })

    it('deve atualizar isConnecting durante conexão', () => {
      const { connectFitbit, isConnecting } = useFitbitAuth()

      delete (window as any).location
      window.location = { href: '' } as any

      connectFitbit()

      expect(isConnecting.value).toBe(true)
    })
  })
})
