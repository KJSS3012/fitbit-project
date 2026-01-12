import mockData from '~/assets/data/fitbit_api_mock_2025_2026.json'
import { startOfDay, endOfDay, isWithinInterval, parseISO, startOfWeek, endOfWeek, startOfMonth, endOfMonth, format } from 'date-fns'

export type TimeFilter = 'daily' | 'weekly' | 'monthly'

interface FitbitApiResponse {
  activity?: {
    summary?: {
      steps?: number
      caloriesOut?: number
    }
  }
  heartrate?: {
    'activities-heart'?: Array<{
      value?: {
        restingHeartRate?: number
      }
    }>
  }
  sleep?: {
    summary?: {
      totalMinutesAsleep?: number
    }
  }
}

export const useFitbitData = () => {
  const config = useRuntimeConfig()
  const { token } = useAuth()
  const { isFitbitConnected } = useFitbitAuth()

  const API_BASE_URL = config.public.apiBase || 'http://localhost:8000'

  const isSimulationMode = useState('fitbit-simulation', () => false)
  const isFitbitMode = useState('fitbit-mode', () => true)
  const realFitbitData = useState<any>('fitbit-real-data', () => null)
  const lastSyncTime = useState<Date | null>('fitbit-last-sync', () => null)

  // Cache for API requests (key: date, value: { data, timestamp })
  const requestCache = useState<Record<string, { data: FitbitApiResponse; timestamp: number }>>('fitbit-request-cache', () => ({}))
  const CACHE_DURATION = 60000 // 1 minute cache

  // Track pending requests to avoid duplicates
  const pendingRequests = useState<Record<string, Promise<FitbitApiResponse | null>>>('fitbit-pending-requests', () => ({}))

  /**
   * Enables Fitbit mode (disables simulation)
   */
  const enableFitbitMode = () => {
    isFitbitMode.value = true
    isSimulationMode.value = false
  }

  /**
   * Enables simulation mode (disables Fitbit)
   */
  const enableSimulationMode = () => {
    isSimulationMode.value = true
    isFitbitMode.value = false
  }

  /**
   * Legacy toggle for backward compatibility
   * @deprecated Use enableFitbitMode or enableSimulationMode instead
   */
  const toggleSimulation = () => {
    if (isSimulationMode.value) {
      enableFitbitMode()
    } else {
      enableSimulationMode()
    }
  }

  /**
   * Fetch real Fitbit data from API with caching and deduplication
   */
  const fetchFitbitData = async (date: string = format(new Date(), 'yyyy-MM-dd')): Promise<FitbitApiResponse | null> => {
    if (!isFitbitConnected.value || !token.value) {
      return null
    }

    // Check cache first
    const cached = requestCache.value[date]
    if (cached && (Date.now() - cached.timestamp) < CACHE_DURATION) {
      return cached.data
    }

    // Check if request is already pending
    if (pendingRequests.value[date]) {
      return pendingRequests.value[date]
    }

    // Create new request
    const request = (async () => {
      try {
        const data = await $fetch<FitbitApiResponse>(`${API_BASE_URL}/fitbit/dashboard`, {
          params: { day: date },
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        })

        // Cache the response
        requestCache.value[date] = {
          data,
          timestamp: Date.now()
        }

        lastSyncTime.value = new Date()
        realFitbitData.value = data
        return data
      } catch (error: any) {
        // Check for 401 token expiration
        if (error?.response?.status === 401 || error?.status === 401) {
          throw new Error('Conexão Fitbit expirou. Reconecte sua conta')
        }

        // Return cached data on error if available
        if (cached) {
          return cached.data
        }

        throw new Error('Falha ao sincronizar. Verifique sua conexão')
      } finally {
        // Clean up pending request
        delete pendingRequests.value[date]
      }
    })()

    // Store pending request
    pendingRequests.value[date] = request
    return request
  }

  /**
   * Synchronize Fitbit data and persist to database
   */
  const syncFitbitData = async (date: string = format(new Date(), 'yyyy-MM-dd')): Promise<boolean> => {
    if (!isFitbitConnected.value || !token.value) {
      throw new Error('Fitbit não está conectado')
    }

    const toast = useToast()

    try {
      const response = await $fetch<{
        success: boolean
        message: string
        data: any
      }>(`${API_BASE_URL}/fitbit/sync`, {
        method: 'POST',
        params: { day: date },
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

      // Update last sync time
      lastSyncTime.value = new Date()

      // Clear cache to force refresh
      delete requestCache.value[date]

      // Show success toast
      toast.add({
        title: 'Sincronização completa',
        description: 'Dados atualizados com sucesso',
        color: 'success',
        icon: 'i-heroicons-check-circle'
      })

      return response.success
    } catch (error: any) {
      // Handle specific error cases
      if (error?.response?.status === 401 || error?.status === 401) {
        const detail = error?.data?.detail || error?.response?.data?.detail || ''
        if (detail.includes('expirou')) {
          toast.add({
            title: 'Conexão expirada',
            description: 'Conexão Fitbit expirou. Reconecte sua conta',
            color: 'error',
            icon: 'i-heroicons-exclamation-circle'
          })
          throw new Error('Conexão Fitbit expirou. Reconecte sua conta')
        }
        toast.add({
          title: 'Não conectado',
          description: 'Fitbit não está conectado',
          color: 'warning',
          icon: 'i-heroicons-exclamation-triangle'
        })
        throw new Error('Fitbit não está conectado')
      }

      toast.add({
        title: 'Falha na sincronização',
        description: 'Falha ao sincronizar dados. Verifique sua conexão',
        color: 'error',
        icon: 'i-heroicons-x-circle'
      })

      throw new Error('Falha ao sincronizar dados. Verifique sua conexão')
    }
  }

  const filterByDateRange = <T extends { dateTime?: string; dateOfSleep?: string }>(
    data: T[],
    startDate: Date,
    endDate: Date
  ): T[] => {
    return data.filter(item => {
      const dateStr = item.dateTime || item.dateOfSleep
      if (!dateStr) return false

      const itemDate = parseISO(dateStr)
      return isWithinInterval(itemDate, { start: startDate, end: endDate })
    })
  }

  const groupByPeriod = <T extends { dateTime?: string; dateOfSleep?: string; value?: string | number }>(
    data: T[],
    period: TimeFilter
  ) => {
    if (period === 'daily') {
      return data.map(item => ({
        date: item.dateTime || item.dateOfSleep || '',
        value: typeof item.value === 'string' ? parseInt(item.value) : (item.value || 0)
      }))
    }

    const grouped = new Map<string, number[]>()

    data.forEach(item => {
      const dateStr = item.dateTime || item.dateOfSleep
      if (!dateStr) return

      const date = parseISO(dateStr)
      let key: string

      if (period === 'weekly') {
        const weekStart = startOfWeek(date, { weekStartsOn: 0 })
        key = weekStart.toISOString().split('T')[0]!
      } else {
        key = startOfMonth(date).toISOString().split('T')[0]!
      }

      const value = typeof item.value === 'string' ? parseInt(item.value) : (item.value || 0)

      if (!grouped.has(key)) {
        grouped.set(key, [])
      }
      grouped.get(key)!.push(value)
    })

    return Array.from(grouped.entries()).map(([date, values]) => ({
      date,
      value: Math.round(values.reduce((a, b) => a + b, 0) / values.length)
    }))
  }

  /**
   * Obtém dados de passos (Prioridade: Fitbit > Simulação)
   */
  const getStepsData = async (startDate: Date, endDate: Date, period: TimeFilter = 'daily') => {
    // Priority 1: Real Fitbit data (only if Fitbit mode enabled and connected)
    if (isFitbitMode.value && isFitbitConnected.value && !isSimulationMode.value) {
      const fitbitData = await fetchFitbitData(format(endDate, 'yyyy-MM-dd'))
      if (fitbitData?.activity?.summary?.steps) {
        return [{
          date: format(endDate, 'yyyy-MM-dd'),
          value: fitbitData.activity.summary.steps
        }]
      }
      // Return empty if Fitbit enabled but no data yet
      return []
    }

    // Priority 2: Simulation fallback (only if simulation mode enabled)
    if (isSimulationMode.value) {
      const filtered = filterByDateRange(mockData['activities-steps'], startDate, endDate)
      return groupByPeriod(filtered, period)
    }

    // No mode enabled or data available
    return []
  }

  /**
   * Obtém dados de batimentos cardíacos (Prioridade: Fitbit > Simulação)
   */
  const getHeartRateData = async (startDate: Date, endDate: Date, period: TimeFilter = 'daily') => {
    // Priority 1: Real Fitbit data (only if Fitbit mode enabled and connected)
    if (isFitbitMode.value && isFitbitConnected.value && !isSimulationMode.value) {
      const fitbitData = await fetchFitbitData(format(endDate, 'yyyy-MM-dd'))
      if (fitbitData?.heartrate?.['activities-heart']?.[0]?.value?.restingHeartRate) {
        return [{
          date: format(endDate, 'yyyy-MM-dd'),
          value: fitbitData.heartrate['activities-heart'][0].value.restingHeartRate
        }]
      }
      // Return empty if Fitbit enabled but no data yet
      return []
    }

    // Priority 2: Simulation fallback (only if simulation mode enabled)
    if (isSimulationMode.value) {
      const heartData = mockData['activities-heart'].map(item => ({
        dateTime: item.dateTime,
        value: item.value?.restingHeartRate || 0
      }))

      const filtered = filterByDateRange(heartData, startDate, endDate)
      return groupByPeriod(filtered, period)
    }

    // No mode enabled or data available
    return []
  }

  /**
   * Obtém dados de sono (Prioridade: Fitbit > Simulação)
   */
  const getSleepData = async (startDate: Date, endDate: Date, period: TimeFilter = 'daily') => {
    // Priority 1: Real Fitbit data (only if Fitbit mode enabled and connected)
    if (isFitbitMode.value && isFitbitConnected.value && !isSimulationMode.value) {
      const fitbitData = await fetchFitbitData(format(endDate, 'yyyy-MM-dd'))
      if (fitbitData?.sleep?.summary?.totalMinutesAsleep) {
        return [{
          date: format(endDate, 'yyyy-MM-dd'),
          value: fitbitData.sleep.summary.totalMinutesAsleep
        }]
      }
      // Return empty if Fitbit enabled but no data yet
      return []
    }

    // Priority 2: Simulation fallback (only if simulation mode enabled)
    if (isSimulationMode.value) {
      const sleepData = mockData.sleep.map(item => {
        const totalMinutes =
          (item.levels?.summary?.deep?.minutes || 0) +
          (item.levels?.summary?.light?.minutes || 0) +
          (item.levels?.summary?.rem?.minutes || 0)

        return {
          dateOfSleep: item.dateOfSleep,
          value: totalMinutes
        }
      })

      const filtered = filterByDateRange(sleepData, startDate, endDate)
      return groupByPeriod(filtered, period)
    }

    // No mode enabled or data available
    return []
  }

  /**
   * Obtém dados de calorias (Prioridade: Fitbit > Simulação)
   */
  const getCaloriesData = async (startDate: Date, endDate: Date, period: TimeFilter = 'daily') => {
    // Priority 1: Real Fitbit data (only if Fitbit mode enabled and connected)
    if (isFitbitMode.value && isFitbitConnected.value && !isSimulationMode.value) {
      const fitbitData = await fetchFitbitData(format(endDate, 'yyyy-MM-dd'))
      if (fitbitData?.activity?.summary?.caloriesOut) {
        return [{
          date: format(endDate, 'yyyy-MM-dd'),
          value: fitbitData.activity.summary.caloriesOut
        }]
      }
      // Return empty if Fitbit enabled but no data yet
      return []
    }

    // Priority 2: Simulation fallback (only if simulation mode enabled)
    if (isSimulationMode.value) {
      const filtered = filterByDateRange(mockData['activities-calories'], startDate, endDate)
      return groupByPeriod(filtered, period)
    }

    // No mode enabled or data available
    return []
  }

  /**
   * Obtém estatísticas resumidas
   */
  const getStats = async (startDate: Date, endDate: Date) => {
    const [stepsData, heartData, sleepData, caloriesData] = await Promise.all([
      getStepsData(startDate, endDate, 'daily'),
      getHeartRateData(startDate, endDate, 'daily'),
      getSleepData(startDate, endDate, 'daily'),
      getCaloriesData(startDate, endDate, 'daily')
    ])

    return {
      steps: {
        total: stepsData.reduce((sum, item) => sum + item.value, 0),
        average: stepsData.length > 0
          ? Math.round(stepsData.reduce((sum, item) => sum + item.value, 0) / stepsData.length)
          : 0,
        max: stepsData.length > 0 ? Math.max(...stepsData.map(d => d.value)) : 0
      },
      heartRate: {
        average: heartData.length > 0
          ? Math.round(heartData.reduce((sum, item) => sum + item.value, 0) / heartData.length)
          : 0,
        min: heartData.length > 0 ? Math.min(...heartData.map(d => d.value)) : 0,
        max: heartData.length > 0 ? Math.max(...heartData.map(d => d.value)) : 0
      },
      sleep: {
        totalHours: Math.round(sleepData.reduce((sum, item) => sum + item.value, 0) / 60),
        averageHours: sleepData.length > 0
          ? (sleepData.reduce((sum, item) => sum + item.value, 0) / sleepData.length / 60).toFixed(1)
          : '0'
      },
      calories: {
        total: caloriesData.reduce((sum, item) => sum + item.value, 0),
        average: caloriesData.length > 0
          ? Math.round(caloriesData.reduce((sum, item) => sum + item.value, 0) / caloriesData.length)
          : 0
      }
    }
  }

  /**
   * Checks if the date range has insufficient data for the selected time filter.
   * Monthly view requires at least 28 days, weekly view requires at least 7 days.
   */
  const hasInsufficientData = (startDate: Date, endDate: Date, period: TimeFilter) => {
    const daysDiff = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))

    if (period === 'monthly' && daysDiff < 28) {
      return true
    }

    if (period === 'weekly' && daysDiff < 7) {
      return true
    }

    return false
  }

  /**
   * Fetches metrics summary from /dashboard/metrics/summary endpoint
   * and checks for stale sleep data (>15 days).
   * Shows toast notification if sleep data is outdated.
   * 
   * @param period - "7d" or "30d"
   */
  const checkSleepDataFreshness = async (period: '7d' | '30d' = '7d') => {
    if (!isFitbitConnected.value || !token.value) {
      return
    }

    try {
      const summary = await $fetch<{
        period: string
        days_analyzed: number
        steps_total: number
        steps_average: number
        steps_max: number
        hr_average: number
        hr_min: number
        hr_max: number
        sleep_total_hours: number
        sleep_average_hours: number
        calories_total: number
        calories_average: number
        last_data_date: string | null
        days_since_last_data: number | null
      }>(`${API_BASE_URL}/dashboard/metrics/summary`, {
        params: { period },
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

      // Check if sleep data is older than 15 days
      if (summary.days_since_last_data !== null && summary.days_since_last_data > 15) {
        const toast = useToast()
        toast.add({
          title: 'Dados de sono desatualizados',
          description: 'Não há dados de sono recentes. Sincronize seu Fitbit para atualizar.',
          color: 'warning',
          icon: 'i-lucide-alert-triangle',
          timeout: 8000
        })
      }
    } catch (error) {
      // Silently fail - this is a non-critical check
      console.warn('Failed to check sleep data freshness:', error)
    }
  }

  return {
    isSimulationMode,
    isFitbitMode,
    lastSyncTime,
    enableFitbitMode,
    enableSimulationMode,
    toggleSimulation,
    fetchFitbitData,
    syncFitbitData,
    getStepsData,
    getHeartRateData,
    getSleepData,
    getCaloriesData,
    getStats,
    hasInsufficientData,
    checkSleepDataFreshness
  }
}
