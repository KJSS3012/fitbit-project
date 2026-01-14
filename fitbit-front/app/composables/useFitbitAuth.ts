export const useFitbitAuth = () => {
  const config = useRuntimeConfig()
  const toast = useToast()
  const { token } = useAuth()

  const API_BASE_URL = config.public.apiBase || 'http://localhost:8000'

  const isFitbitConnected = useState('fitbitConnected', () => false)
  const isConnecting = useState('fitbitConnecting', () => false)

  /**
   * Initiates Fitbit OAuth flow
   * Browser automatically sends auth_token cookie to backend
   * Backend extracts CPF from JWT token
   */
  /**
   * Initiates Fitbit OAuth flow
   * Gets OAuth URL from backend and redirects
   */
  const connectFitbit = async () => {
    if (!token.value) {
      toast.add({
        title: 'Erro de autenticação',
        description: 'Você precisa estar logado para conectar o Fitbit',
        color: 'error',
        icon: 'i-heroicons-x-circle'
      })
      return
    }

    isConnecting.value = true

    toast.add({
      title: 'Redirecionando para Fitbit',
      description: 'Você será redirecionado para autorizar o acesso',
      color: 'info',
      icon: 'i-simple-icons-fitbit'
    })

    try {
      // Get OAuth URL from backend (requires JWT authentication)
      const response = await fetch(`${API_BASE_URL}/fitbit/auth`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to get OAuth URL: ${response.statusText}`)
      }

      const data = await response.json()
      if (data.url) {
        window.location.href = data.url
      } else {
        throw new Error('No OAuth URL received from server')
      }
    } catch (error) {
      console.error('Error initiating Fitbit connection:', error)
      toast.add({
        title: 'Erro ao conectar',
        description: 'Não foi possível iniciar a conexão com o Fitbit',
        color: 'error',
        icon: 'i-heroicons-x-circle'
      })
      isConnecting.value = false
    }
  }

  /**
   * Checks if Fitbit is connected
   */
  const checkFitbitStatus = async () => {
    try {
      const { token } = useAuth()
      const route = useRoute()

      // Check URL query first for immediate feedback
      if (route.query.fitbit === 'connected') {
        toast.add({
          title: 'Fitbit conectado com sucesso!',
          description: 'Seus dados Fitbit estão sendo sincronizados',
          color: 'success',
          icon: 'i-heroicons-check-circle'
        })

        // Clean URL
        const router = useRouter()
        router.replace({ query: {} })

        // Verify actual connection status with API
        if (token.value) {
          const response = await fetch(`${API_BASE_URL}/fitbit/status`, {
            headers: {
              'Authorization': `Bearer ${token.value}`,
              'Content-Type': 'application/json'
            }
          })

          if (response.ok) {
            const data = await response.json()
            isFitbitConnected.value = data.connected
          }
        }
        return
      }

      // User denied access
      if (route.query.fitbit === 'denied') {
        isFitbitConnected.value = false
        isConnecting.value = false

        toast.add({
          title: 'Conexão cancelada pelo usuário',
          description: 'Você pode tentar conectar novamente quando quiser',
          color: 'warning',
          icon: 'i-heroicons-exclamation-triangle'
        })

        // Clean URL
        const router = useRouter()
        router.replace({ query: {} })
        return
      }

      // Server/token error
      if (route.query.fitbit === 'error') {
        isFitbitConnected.value = false
        isConnecting.value = false

        toast.add({
          title: 'Erro ao finalizar conexão',
          description: 'Tente novamente mais tarde',
          color: 'error',
          icon: 'i-heroicons-x-circle'
        })

        // Clean URL
        const router = useRouter()
        router.replace({ query: {} })
        return
      }

      // Check actual connection status from API
      if (token.value) {
        const response = await fetch(`${API_BASE_URL}/fitbit/status`, {
          headers: {
            'Authorization': `Bearer ${token.value}`,
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const data = await response.json()
          isFitbitConnected.value = data.connected
        } else {
          console.error('Failed to check Fitbit status:', response.status, response.statusText)
          isFitbitConnected.value = false
        }
      }
    } catch (error) {
      console.error('Error checking Fitbit status:', error)
      isFitbitConnected.value = false
    }
  }

  /**
   * Disconnects Fitbit account
   */
  const disconnectFitbit = async () => {
    try {
      const { token } = useAuth()

      if (!token.value) {
        throw new Error('No token')
      }

      const response = await fetch(`${API_BASE_URL}/fitbit/disconnect`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to disconnect: ${response.statusText}`)
      }

      isFitbitConnected.value = false

      toast.add({
        title: 'Fitbit desconectado',
        description: 'Você pode reconectar a qualquer momento',
        color: 'neutral',
        icon: 'i-simple-icons-fitbit'
      })
    } catch (error) {
      console.error('Error disconnecting Fitbit:', error)
      toast.add({
        title: 'Erro ao desconectar',
        description: 'Tente novamente',
        color: 'error',
        icon: 'i-heroicons-exclamation-circle'
      })
    }
  }

  return {
    isFitbitConnected,
    isConnecting,
    connectFitbit,
    checkFitbitStatus,
    disconnectFitbit
  }
}
