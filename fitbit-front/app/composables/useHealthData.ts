import { createSharedComposable } from '@vueuse/core'

const _useHealthData = () => {
  const config = useRuntimeConfig()
  const { token } = useAuth()

  const API_BASE_URL = config.public.apiBase
  const useMockData = useState('useMockData', () => false)

  /**
   * Fetches patient health data from mock or real API based on useMockData flag
   */
  const getHealthData = async (patientId: string, dateRange?: { start: string; end: string }): Promise<any | null> => {
    if (useMockData.value) {
      try {
        const mockData = await import('~/assets/data/fitbit_api_mock_2025_2026.json')
        return mockData.default
      } catch (error) {
        console.error('Error loading mock data:', error)
        return null
      }
    }

    try {
      const response = await $fetch<any>(`${API_BASE_URL}/fitbit/data/${patientId}`, {
        headers: {
          Authorization: `Bearer ${token.value}`
        },
        query: dateRange
      })

      return response
    } catch (error) {
      console.error('Error fetching health data:', error)
      return null
    }
  }

  /**
   * Fetches activity data (steps, calories, distance)
   */
  const getActivities = async (patientId: string, dateRange?: { start: string; end: string }) => {
    if (useMockData.value) {
      try {
        const mockData = await import('~/assets/data/fitbit_api_mock_2025_2026.json')
        return {
          steps: mockData.default['activities-steps'] || [],
          calories: mockData.default['activities-calories'] || [],
          distance: mockData.default['activities-distance'] || []
        }
      } catch (error) {
        console.error('Error loading mock activities:', error)
        return null
      }
    }

    try {
      const response = await $fetch(`${API_BASE_URL}/fitbit/activities/${patientId}`, {
        headers: {
          Authorization: `Bearer ${token.value}`
        },
        query: dateRange
      })

      return response
    } catch (error) {
      console.error('Error fetching activities:', error)
      return null
    }
  }

  /**
   * Fetches heart rate data
   */
  const getHeartRate = async (patientId: string, dateRange?: { start: string; end: string }) => {
    if (useMockData.value) {
      try {
        const mockData = await import('~/assets/data/fitbit_api_mock_2025_2026.json')
        return mockData.default['activities-heart'] || []
      } catch (error) {
        console.error('Error loading mock heart rate:', error)
        return null
      }
    }

    try {
      const response = await $fetch(`${API_BASE_URL}/fitbit/heart-rate/${patientId}`, {
        headers: {
          Authorization: `Bearer ${token.value}`
        },
        query: dateRange
      })

      return response
    } catch (error) {
      console.error('Error fetching heart rate:', error)
      return null
    }
  }

  /**
   * Fetches sleep data
   */
  const getSleep = async (patientId: string, dateRange?: { start: string; end: string }) => {
    if (useMockData.value) {
      try {
        const mockData = await import('~/assets/data/fitbit_api_mock_2025_2026.json')
        return mockData.default.sleep || []
      } catch (error) {
        console.error('Error loading mock sleep:', error)
        return null
      }
    }

    try {
      const response = await $fetch(`${API_BASE_URL}/fitbit/sleep/${patientId}`, {
        headers: {
          Authorization: `Bearer ${token.value}`
        },
        query: dateRange
      })

      return response
    } catch (error) {
      console.error('Error fetching sleep data:', error)
      return null
    }
  }

  return {
    getHealthData,
    getActivities,
    getHeartRate,
    getSleep,
    useMockData
  }
}

export const useHealthData = createSharedComposable(_useHealthData)
