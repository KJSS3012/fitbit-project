export interface User {
  id: string
  name: string
  email: string
  type: 'paciente' | 'medico'
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  user_type: string
  cpf: string
  name: string
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
    userType: 'paciente' | 'medico',
    cpf: string,
    password: string,
    rememberMe = false
  ) => {
    try {
      const endpoint =
        userType === 'medico'
          ? `${API_BASE_URL}/auth/login/doctor`
          : `${API_BASE_URL}/auth/login/patient`

      const response = await $fetch<any>(endpoint, {
        method: 'POST',
        body: {
          cpf,
          password
        }
      })

      // Salva um token simples (pode ser o CPF ou CRM por enquanto)
      // TODO: Implementar JWT no backend
      token.value = cpf

      // Salva os dados do usuário
      user.value = {
        id: response.cpf || response.crm,
        name: response.name,
        email: response.email || '',
        type: userType
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
      // Define o endpoint baseado no tipo de usuário
      const endpoint = data.user_type === 'medico'
        ? `${API_BASE_URL}/auth/register/doctor`
        : `${API_BASE_URL}/auth/register/patient`

      const response = await $fetch<{ message: string; user: User }>(endpoint, {
        method: 'POST',
        body: data,
        headers: {
          'Content-Type': 'application/json'
        }
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
  const isAuthenticated = computed(() => !!token.value)

  /**
   * Verifica se o usuário é médico
   */
  const isDoctor = computed(() => user.value?.type === 'medico')

  /**
   * Verifica se o usuário é paciente
   */
  const isPatient = computed(() => user.value?.type === 'paciente')

  return {
    user: readonly(user),
    token: readonly(token),
    isAuthenticated,
    isDoctor,
    isPatient,
    login,
    register,
    logout,
    fetchUser
  }
}
