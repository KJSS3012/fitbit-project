import mockData from '~/assets/data/fitbit_api_mock_2025_2026.json'
import { startOfDay, endOfDay, isWithinInterval, parseISO, startOfWeek, endOfWeek, startOfMonth, endOfMonth } from 'date-fns'

export type TimeFilter = 'daily' | 'weekly' | 'monthly'

export const useFitbitData = () => {
  const isSimulationMode = useState('fitbit-simulation', () => false)

  const toggleSimulation = () => {
    isSimulationMode.value = !isSimulationMode.value
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
   * Obtém dados de passos
   */
  const getStepsData = (startDate: Date, endDate: Date, period: TimeFilter = 'daily') => {
    if (!isSimulationMode.value) {
      // TODO: Buscar dados reais da API
      return []
    }

    const filtered = filterByDateRange(mockData['activities-steps'], startDate, endDate)
    return groupByPeriod(filtered, period)
  }

  /**
   * Obtém dados de batimentos cardíacos
   */
  const getHeartRateData = (startDate: Date, endDate: Date, period: TimeFilter = 'daily') => {
    if (!isSimulationMode.value) {
      return []
    }

    const heartData = mockData['activities-heart'].map(item => ({
      dateTime: item.dateTime,
      value: item.value?.restingHeartRate || 0
    }))

    const filtered = filterByDateRange(heartData, startDate, endDate)
    return groupByPeriod(filtered, period)
  }

  /**
   * Obtém dados de sono (em minutos)
   */
  const getSleepData = (startDate: Date, endDate: Date, period: TimeFilter = 'daily') => {
    if (!isSimulationMode.value) {
      return []
    }

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

  /**
   * Obtém dados de calorias
   */
  const getCaloriesData = (startDate: Date, endDate: Date, period: TimeFilter = 'daily') => {
    if (!isSimulationMode.value) {
      return []
    }

    const filtered = filterByDateRange(mockData['activities-calories'], startDate, endDate)
    return groupByPeriod(filtered, period)
  }

  /**
   * Obtém estatísticas resumidas
   */
  const getStats = (startDate: Date, endDate: Date) => {
    const stepsData = getStepsData(startDate, endDate, 'daily')
    const heartData = getHeartRateData(startDate, endDate, 'daily')
    const sleepData = getSleepData(startDate, endDate, 'daily')
    const caloriesData = getCaloriesData(startDate, endDate, 'daily')

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
          : 0
      },
      calories: {
        total: caloriesData.reduce((sum, item) => sum + item.value, 0),
        average: caloriesData.length > 0
          ? Math.round(caloriesData.reduce((sum, item) => sum + item.value, 0) / caloriesData.length)
          : 0
      }
    }
  }


  const hasInsufficientData = (startDate: Date, endDate: Date, period: TimeFilter) => {
    const daysDiff = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))

    // Para visualização mensal, precisa de pelo menos 28 dias
    if (period === 'monthly' && daysDiff < 28) {
      return true
    }

    // Para visualização semanal, precisa de pelo menos 7 dias
    if (period === 'weekly' && daysDiff < 7) {
      return true
    }

    return false
  }

  return {
    isSimulationMode,
    toggleSimulation,
    getStepsData,
    getHeartRateData,
    getSleepData,
    getCaloriesData,
    getStats,
    hasInsufficientData
  }
}
