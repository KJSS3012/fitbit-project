// services/api.ts
import { useFetch } from '#app'

const BASE_URL = 'http://localhost:8000'

interface RegisterPayload {
  user_type: string
  cpf: string
  name: string
  crm?: string
  password: string
}

export const register = async (payload: RegisterPayload) => {
  const endpoint =
    payload.user_type === 'paciente'
      ? '/auth/register/patient'
      : '/auth/register/doctor'

  const { data, error } = await useFetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    body: payload,
  })

  if (error.value) {
    throw new Error(error.value?.message || 'Erro ao criar conta')
  }

  return data.value
}

interface LoginPayload {
  user_type: 'paciente' | 'medico'
  identifier: string
  password: string
  rememberMe?: boolean
}

export const login = async (payload: LoginPayload) => {
  const endpoint = '/auth/login'
  const { data, error } = await useFetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    body: payload,
  })

  if (error.value) {
    throw new Error(error.value?.message || 'Erro ao fazer login')
  }

  return data.value
}
