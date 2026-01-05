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

      // Faz a requisição - só precisa retornar sucesso
      await $fetch<any>(endpoint, {
        method: 'POST',
        body: {
          cpf,
          password
        }
      })

      // Se chegou aqui, o login foi bem-sucedido
      // Cria um objeto de usuário simulado baseado nos dados do login
      token.value = cpf

      user.value = {
        id: cpf,
        name: `Usuário ${userType === 'medico' ? 'Médico' : 'Paciente'}`,
        email: `${cpf}@example.com`,
        type: userType
      }

      return { success: true }
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

      // Faz a requisição - só precisa retornar sucesso
      await $fetch<any>(endpoint, {
        method: 'POST',
        body: data,
        headers: {
          'Content-Type': 'application/json'
        }
      })

      // Se chegou aqui, o registro foi bem-sucedido
      return {
        message: 'Conta criada com sucesso',
        success: true
      }
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

    // Como estamos simulando, não precisa chamar a API
    // O user já foi criado no login
    if (user.value) {
      return user.value
    }

    // Se por algum motivo o user não existe mas tem token, limpa tudo
    token.value = null
    return null
  }

  /**
   * Verifica se o usuário está autenticado
   */
  const isAuthenticated = computed(() => !!token.value && !!user.value)

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
