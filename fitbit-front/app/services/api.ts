import { useFetch } from '#app'

const BASE_URL = 'http://localhost:8000'

interface RegisterPayload {
  user_type: 'paciente' | 'medico'
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

  // remove user_type antes de enviar
  const { user_type, ...body } = payload

  const { data, error } = await useFetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    body,
  })

  if (error.value) {
    throw new Error(error.value?.data?.detail || 'Erro ao criar conta')
  }

  return data.value
}

interface LoginPayload {
  user_type: 'paciente' | 'medico'
  cpf: string
  password: string
}

export const login = async (payload: LoginPayload) => {
  const endpoint =
    payload.user_type === 'paciente'
      ? '/auth/login/patient'
      : '/auth/login/doctor'

  const { user_type, ...body } = payload

  const { data, error } = await useFetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    body,
  })

  if (error.value) {
    throw new Error(error.value?.data?.detail || 'Erro ao fazer login')
  }

  return data.value
}
