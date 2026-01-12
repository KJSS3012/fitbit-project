export const useFitbitAuth = () => {
  const config = useRuntimeConfig()
  const toast = useToast()

  const API_BASE_URL = config.public.apiBase || 'http://localhost:8000'

  const isFitbitConnected = useState('fitbitConnected', () => false)
  const isConnecting = useState('fitbitConnecting', () => false)
  const fitbitAuthUrl = `${API_BASE_URL}/fitbit/auth`

  /**
   * Initiates Fitbit OAuth flow
   */
  const connectFitbit = () => {
    isConnecting.value = true

    toast.add({
      title: 'Redirecionando para Fitbit',
      description: 'Você será redirecionado para autorizar o acesso',
      color: 'info',
      icon: 'i-simple-icons-fitbit'
    })

    // Redirect to backend OAuth endpoint
    setTimeout(() => {
      window.location.href = fitbitAuthUrl
    }, 500)
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
        isFitbitConnected.value = true

        toast.add({
          title: 'Fitbit conectado com sucesso!',
          description: 'Seus dados Fitbit estão sendo sincronizados',
          color: 'success',
          icon: 'i-heroicons-check-circle'
        })

        // Clean URL
        const router = useRouter()
        router.replace({ query: {} })
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
        const response = await $fetch<{ connected: boolean }>(`${API_BASE_URL}/fitbit/status`, {
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        })

        isFitbitConnected.value = response.connected
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

      await $fetch(`${API_BASE_URL}/fitbit/disconnect`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

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
