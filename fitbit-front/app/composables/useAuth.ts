export interface User {
  id: string
  name: string
  email: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  user_type: string
  cpf: string
  crm?: string
  password: string
}

export const useAuth = () => {
  const config = useRuntimeConfig()
  const user = useState<User | null>('user', () => null)
  const token = useCookie('auth_token', {
    maxAge: 60 * 60 * 24 * 7 // 7 dias
  })

  const API_BASE_URL = config.public.apiBase

  /**
   * Realiza o login do usuário
   */
  const login = async (
    userType: string,
    identifier: string,
    password: string,
    rememberMe: boolean = false
  ) => {
    try {
      const response = await $fetch<{ access_token: string; user: User }>(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        body: {
          user_type: userType,
          identifier,
          password
        }
      })

      // Armazena o token
      token.value = response.access_token

      // Atualiza o estado do usuário
      user.value = response.user

      // Se rememberMe for true, o cookie já persiste por 7 dias
      // Caso contrário, podemos ajustar a duração
      if (!rememberMe) {
        token.value = response.access_token
        // Cookie expira ao fechar o navegador
      }

      return response
    } catch (error: any) {
      console.error('Login error:', error)
      throw new Error(error.data?.detail || 'Erro ao fazer login')
    }
  }

  /**
   * Registra um novo usuário
   */
  const register = async (data: RegisterData) => {
    try {
      const response = await $fetch<{ message: string; user: User }>(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        body: data
      })

      return response
    } catch (error: any) {
      console.error('Register error:', error)
      throw new Error(error.data?.detail || 'Erro ao criar conta')
    }
  }

  /**
   * Faz logout do usuário
   */
  const logout = async () => {
    try {
      // Opcional: chamar endpoint de logout no backend
      // await $fetch(`${API_BASE_URL}/auth/logout`, {
      //   method: 'POST',
      //   headers: {
      //     Authorization: `Bearer ${token.value}`
      //   }
      // })

      // Limpa o token e o estado do usuário
      token.value = null
      user.value = null

      // Redireciona para login
      await navigateTo('/auth/login')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  /**
   * Busca os dados do usuário autenticado
   */
  const fetchUser = async () => {
    if (!token.value) {
      return null
    }

    try {
      const response = await $fetch<User>(`${API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

      user.value = response
      return response
    } catch (error) {
      console.error('Fetch user error:', error)
      // Se o token é inválido, limpa tudo
      token.value = null
      user.value = null
      return null
    }
  }

  /**
   * Verifica se o usuário está autenticado
   */
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  return {
    user: readonly(user),
    token: readonly(token),
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser
  }
}
