/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockConfig = { public: { apiBaseUrl: 'http://localhost:8000' } }
const mockToken = { value: 'test-token' }
const mockIsFitbitConnected = { value: false }

vi.stubGlobal('useRuntimeConfig', () => mockConfig)
vi.stubGlobal('useAuth', () => ({ token: mockToken }))
vi.stubGlobal('useFitbitAuth', () => ({ isFitbitConnected: mockIsFitbitConnected }))
vi.stubGlobal('useState', (key: string, init?: () => any) => {
  const states: Record<string, any> = {
    'fitbit-simulation': { value: false },
    'fitbit-mode': { value: true },
    'fitbit-real-data': { value: null }
  }
  return states[key] || { value: init ? init() : null }
})

  ; (global as any).$fetch = vi.fn()

import { useFitbitData } from './useFitbitData'

describe('useFitbitData - Toggle Exclusivo', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('deve inicializar com Fitbit mode ativo e simulação desativada', () => {
    const { isFitbitMode, isSimulationMode } = useFitbitData()

    expect(isFitbitMode.value).toBe(true)
    expect(isSimulationMode.value).toBe(false)
  })

  it('enableFitbitMode deve ativar Fitbit e desativar simulação', () => {
    const { enableFitbitMode, isFitbitMode, isSimulationMode } = useFitbitData()

    // Simular modo simulação ativo
    isSimulationMode.value = true
    isFitbitMode.value = false

    enableFitbitMode()

    expect(isFitbitMode.value).toBe(true)
    expect(isSimulationMode.value).toBe(false)
  })

  it('enableSimulationMode deve ativar simulação e desativar Fitbit', () => {
    const { enableSimulationMode, isFitbitMode, isSimulationMode } = useFitbitData()

    enableSimulationMode()

    expect(isSimulationMode.value).toBe(true)
    expect(isFitbitMode.value).toBe(false)
  })

  it('toggleSimulation deve alternar entre modos de forma exclusiva', () => {
    const { toggleSimulation, isFitbitMode, isSimulationMode } = useFitbitData()

    // Inicialmente Fitbit ativo
    expect(isFitbitMode.value).toBe(true)
    expect(isSimulationMode.value).toBe(false)

    // Toggle para simulação
    toggleSimulation()
    expect(isSimulationMode.value).toBe(true)
    expect(isFitbitMode.value).toBe(false)

    // Toggle de volta para Fitbit
    toggleSimulation()
    expect(isFitbitMode.value).toBe(true)
    expect(isSimulationMode.value).toBe(false)
  })

  it('getStepsData deve retornar vazio quando Fitbit ativo mas não conectado', async () => {
    mockIsFitbitConnected.value = false
    const { getStepsData, enableFitbitMode } = useFitbitData()

    enableFitbitMode()

    const data = await getStepsData(new Date('2026-01-01'), new Date('2026-01-07'), 'daily')

    expect(data).toEqual([])
  })

  it('getStepsData deve retornar dados simulados quando simulação ativa', async () => {
    const { getStepsData, enableSimulationMode } = useFitbitData()

    enableSimulationMode()

    const data = await getStepsData(new Date('2025-01-01'), new Date('2025-01-07'), 'daily')

    expect(data.length).toBeGreaterThan(0)
    expect(data[0]).toHaveProperty('date')
    expect(data[0]).toHaveProperty('value')
  })

  it('getStepsData deve chamar API quando Fitbit ativo e conectado', async () => {
    mockIsFitbitConnected.value = true
      ; (global.$fetch as any).mockResolvedValue({
        activity: { summary: { steps: 10000 } }
      })

    const { getStepsData, enableFitbitMode } = useFitbitData()

    enableFitbitMode()

    const data = await getStepsData(new Date('2026-01-01'), new Date('2026-01-01'), 'daily')

    expect(global.$fetch).toHaveBeenCalled()
    expect(data).toHaveLength(1)
    expect(data[0]?.value).toBe(10000)
  })

  it('getHeartRateData deve respeitar modo exclusivo', async () => {
    const { getHeartRateData, enableSimulationMode, enableFitbitMode } = useFitbitData()

    // Modo simulação
    enableSimulationMode()
    const simData = await getHeartRateData(new Date('2025-01-01'), new Date('2025-01-07'), 'daily')
    expect(simData.length).toBeGreaterThan(0)

    // Modo Fitbit sem conexão
    mockIsFitbitConnected.value = false
    enableFitbitMode()
    const fitbitData = await getHeartRateData(new Date('2026-01-01'), new Date('2026-01-07'), 'daily')
    expect(fitbitData).toEqual([])
  })

  it('não deve misturar dados de Fitbit e simulação', async () => {
    mockIsFitbitConnected.value = true
      ; (global.$fetch as any).mockResolvedValue({
        activity: { summary: { steps: 5000 } }
      })

    const { getStepsData, isFitbitMode, isSimulationMode } = useFitbitData()

    // Garantir apenas um modo ativo
    expect(isFitbitMode.value && isSimulationMode.value).toBe(false)

    const data = await getStepsData(new Date('2026-01-01'), new Date('2026-01-01'), 'daily')

    // Se Fitbit ativo, deve ter exatamente 1 registro (dados reais)
    if (isFitbitMode.value) {
      expect(data).toHaveLength(1)
      expect(data[0]?.value).toBe(5000)
    }
  })
})

describe('useFitbitData - Sleep Data Freshness Check', () => {
  const mockToast = {
    add: vi.fn()
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.stubGlobal('useToast', () => mockToast)
    mockIsFitbitConnected.value = true
    mockToken.value = 'test-token'
  })

  it('deve mostrar toast quando sleep data > 15 dias', async () => {
    const { checkSleepDataFreshness } = useFitbitData()

      ; (global as any).$fetch = vi.fn().mockResolvedValue({
        period: '7d',
        days_analyzed: 7,
        steps_total: 50000,
        steps_average: 7142,
        steps_max: 12000,
        hr_average: 72,
        hr_min: 60,
        hr_max: 85,
        sleep_total_hours: 50.5,
        sleep_average_hours: 7.2,
        calories_total: 14000,
        calories_average: 2000,
        last_data_date: '2025-12-10',
        days_since_last_data: 20 // > 15 days
      })

    await checkSleepDataFreshness('7d')

    expect(mockToast.add).toHaveBeenCalledWith({
      title: 'Dados de sono desatualizados',
      description: 'Não há dados de sono recentes. Sincronize seu Fitbit para atualizar.',
      color: 'warning',
      icon: 'i-lucide-alert-triangle'
    })
  })

  it('NÃO deve mostrar toast quando sleep data <= 15 dias', async () => {
    const { checkSleepDataFreshness } = useFitbitData()

      ; (global as any).$fetch = vi.fn().mockResolvedValue({
        period: '7d',
        days_analyzed: 7,
        last_data_date: '2026-01-05',
        days_since_last_data: 6 // <= 15 days, OK
      })

    await checkSleepDataFreshness('7d')

    expect(mockToast.add).not.toHaveBeenCalled()
  })

  it('deve falhar silenciosamente se Fitbit não conectado', async () => {
    const { checkSleepDataFreshness } = useFitbitData()
    mockIsFitbitConnected.value = false

    await checkSleepDataFreshness('7d')

    expect((global as any).$fetch).not.toHaveBeenCalled()
    expect(mockToast.add).not.toHaveBeenCalled()
  })
})

