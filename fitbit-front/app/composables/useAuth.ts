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
   * Decodes JWT token to extract user information
   */
  const decodeToken = (jwt: string) => {
    try {
      const base64Url = jwt.split('.')[1]
      if (!base64Url) {
        return null
      }
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
      return JSON.parse(jsonPayload)
    } catch (error) {
      console.error('Error decoding token:', error)
      return null
    }
  }

  /**
   * Authenticates user and stores JWT token
   */
  const login = async (
    userType: 'paciente' | 'medico',
    identifier: string,
    password: string,
    rememberMe = false
  ) => {
    try {
      const endpoint =
        userType === 'medico'
          ? `${API_BASE_URL}/auth/login/doctor`
          : `${API_BASE_URL}/auth/login/patient`

      const body = userType === 'medico'
        ? { crm: identifier, password }
        : { cpf: identifier, password }

      const response = await $fetch<{ access_token: string; token_type: string }>(endpoint, {
        method: 'POST',
        body
      })

      token.value = response.access_token
      const decoded = decodeToken(response.access_token)

      if (decoded) {
        user.value = {
          id: decoded.sub,
          name: '',
          email: `${decoded.sub}@example.com`,
          type: userType
        }
      }

      return response
    } catch (error: any) {
      console.error('Login error:', error)
      throw new Error(error.data?.detail || 'Erro ao fazer login')
    }
  }

  /**
   * Registers a new user
   */
  const register = async (data: RegisterData) => {
    try {
      const endpoint = data.user_type === 'medico'
        ? `${API_BASE_URL}/auth/register/doctor`
        : `${API_BASE_URL}/auth/register/patient`

      const { user_type, ...bodyData } = data

      const response = await $fetch<any>(endpoint, {
        method: 'POST',
        body: bodyData,
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
   * Logs out user and clears authentication state
   */
  const logout = async () => {
    try {
      token.value = null
      user.value = null
      await navigateTo('/auth/login')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  /**
   * Fetches authenticated user data from token
   */
  const fetchUser = async () => {
    if (!token.value) {
      return null
    }

    const decoded = decodeToken(token.value)

    if (decoded) {
      user.value = {
        id: decoded.sub,
        name: '',
        email: `${decoded.sub}@example.com`,
        type: decoded.type === 'patient' ? 'paciente' : 'medico'
      }
      return user.value
    }

    token.value = null
    return null
  }

  const isAuthenticated = computed(() => !!token.value)
  const isDoctor = computed(() => user.value?.type === 'medico')
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
