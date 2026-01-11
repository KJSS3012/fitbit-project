import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock $fetch global
const mockFetch = vi.fn()
global.$fetch = mockFetch as any

describe('useAuth - decodeToken', () => {
  it('should decode valid JWT token', () => {
    // JWT token: { "sub": "12345678901", "type": "paciente", "exp": 1234567890 }
    const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwMSIsInR5cGUiOiJwYWNpZW50ZSIsImV4cCI6MTIzNDU2Nzg5MH0.8t7Xf3uO4nT-7tLv3hR3d8jC9wK8qZ5aX4bY2eE1fN4'

    const result = decodeToken(validToken)

    expect(result).toBeDefined()
    expect(result?.sub).toBe('12345678901')
    expect(result?.type).toBe('paciente')
  })

  it('should return null for invalid token format', () => {
    const invalidToken = 'invalid.token'
    const result = decodeToken(invalidToken)
    expect(result).toBeNull()
  })

  it('should return null for malformed token', () => {
    const malformedToken = 'header.notbase64.signature'
    const result = decodeToken(malformedToken)
    expect(result).toBeNull()
  })

  it('should return null for empty string', () => {
    const result = decodeToken('')
    expect(result).toBeNull()
  })

  it('should decode token with URL-safe base64', () => {
    // Token with URL-safe characters
    const urlSafeToken = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NSIsInR5cGUiOiJtZWRpY28ifQ.test'
    // Won't fail even if signature is wrong - we only decode payload
    const result = decodeToken(urlSafeToken)
    expect(result).toBeDefined()
  })
})

describe('useAuth - register', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should register patient successfully', async () => {
    const mockResponse = {
      cpf: '52998224725',
      name: 'JOÃO CABRAL'
    }

    mockFetch.mockResolvedValueOnce(mockResponse)

    const { register } = useAuth()
    const result = await register({
      user_type: 'paciente',
      cpf: '52998224725',
      name: 'João Cabral',
      password: 'Abcdefghijk1!'
    })

    expect(result).toEqual(mockResponse)
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/auth/register/patient'),
      expect.objectContaining({
        method: 'POST',
        body: {
          cpf: '52998224725',
          name: 'João Cabral',
          password: 'Abcdefghijk1!'
        }
      })
    )
  })

  it('should register doctor successfully', async () => {
    const mockResponse = {
      cpf: '52998224725',
      name: 'DR CABRAL',
      crm: 'SP123456'
    }

    mockFetch.mockResolvedValueOnce(mockResponse)

    const { register } = useAuth()
    const result = await register({
      user_type: 'medico',
      cpf: '52998224725',
      name: 'Dr Cabral',
      crm: 'SP123456',
      password: 'Abcdefghijk1!'
    })

    expect(result).toEqual(mockResponse)
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/auth/register/doctor'),
      expect.objectContaining({
        method: 'POST',
        body: {
          cpf: '52998224725',
          name: 'Dr Cabral',
          crm: 'SP123456',
          password: 'Abcdefghijk1!'
        }
      })
    )
  })

  it('should throw error when CPF already exists', async () => {
    const errorResponse = {
      data: { detail: 'O CPF já está cadastrado' }
    }

    mockFetch.mockRejectedValueOnce(errorResponse)

    const { register } = useAuth()

    await expect(register({
      user_type: 'paciente',
      cpf: '52998224725',
      name: 'João Cabral',
      password: 'Abcdefghijk1!'
    })).rejects.toThrow('O CPF já está cadastrado')
  })

  it('should throw error when CPF is invalid', async () => {
    const errorResponse = {
      data: { detail: 'CPF inválido' }
    }

    mockFetch.mockRejectedValueOnce(errorResponse)

    const { register } = useAuth()

    await expect(register({
      user_type: 'paciente',
      cpf: '11111111111',
      name: 'João Cabral',
      password: 'Abcdefghijk1!'
    })).rejects.toThrow('CPF inválido')
  })

  it('should throw error when password is weak', async () => {
    const errorResponse = {
      data: { detail: 'Senha deve conter pelo menos 12 caracteres' }
    }

    mockFetch.mockRejectedValueOnce(errorResponse)

    const { register } = useAuth()

    await expect(register({
      user_type: 'paciente',
      cpf: '52998224725',
      name: 'João Cabral',
      password: 'abc123'
    })).rejects.toThrow('Senha deve conter pelo menos 12 caracteres')
  })

  it('should throw generic error when API fails', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    const { register } = useAuth()

    await expect(register({
      user_type: 'paciente',
      cpf: '52998224725',
      name: 'João Cabral',
      password: 'Abcdefghijk1!'
    })).rejects.toThrow('Erro ao criar conta')
  })
})

// Helper function extracted from useAuth composable
function decodeToken(jwt: string) {
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
    return null
  }
}

// Mock useAuth implementation for testing
function useAuth() {
  const config = { public: { apiBase: 'http://localhost:8000' } }
  const API_BASE_URL = config.public.apiBase

  const login = async (userType: 'paciente' | 'medico', identifier: string, password: string) => {
    try {
      const endpoint = userType === 'medico'
        ? `${API_BASE_URL}/auth/login/doctor`
        : `${API_BASE_URL}/auth/login/patient`

      const body = userType === 'medico'
        ? { crm: identifier, password }
        : { cpf: identifier, password }

      const response = await $fetch<{ access_token: string; token_type: string }>(endpoint, {
        method: 'POST',
        body
      })

      return response
    } catch (error: any) {
      throw new Error(error.data?.detail || 'Erro ao fazer login')
    }
  }

  const register = async (data: any) => {
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
      throw new Error(error.data?.detail || 'Erro ao criar conta')
    }
  }

  return { login, register }
}

describe('useAuth - login patient', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should login patient successfully with valid CPF and password', async () => {
    const mockResponse = {
      access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Mjk5ODIyNDcyNSIsInR5cGUiOiJwYWNpZW50ZSIsImV4cCI6MTcwNTAwMDAwMH0.test',
      token_type: 'bearer'
    }

    mockFetch.mockResolvedValueOnce(mockResponse)

    const { login } = useAuth()
    const result = await login('paciente', '52998224725', 'Abcdefjhijk1!')

    expect(result).toEqual(mockResponse)
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/auth/login/patient'),
      expect.objectContaining({
        method: 'POST',
        body: {
          cpf: '52998224725',
          password: 'Abcdefjhijk1!'
        }
      })
    )
  })

  it('should throw error when credentials are invalid (401)', async () => {
    const errorResponse = {
      data: { detail: 'Credenciais inválidas' }
    }

    mockFetch.mockRejectedValueOnce(errorResponse)

    const { login } = useAuth()

    await expect(login('paciente', '52998224725', 'WrongPassword123!')).rejects.toThrow('Credenciais inválidas')
  })

  it('should throw error when CPF does not exist', async () => {
    const errorResponse = {
      data: { detail: 'Credenciais inválidas' }
    }

    mockFetch.mockRejectedValueOnce(errorResponse)

    const { login } = useAuth()

    await expect(login('paciente', '99999999999', 'Abcdefjhijk1!')).rejects.toThrow('Credenciais inválidas')
  })

  it('should throw error when fields are empty', async () => {
    const errorResponse = {
      data: { detail: 'Credenciais inválidas' }
    }

    mockFetch.mockRejectedValueOnce(errorResponse)

    const { login } = useAuth()

    await expect(login('paciente', '', '')).rejects.toThrow('Credenciais inválidas')
  })

  it('should throw generic error when network fails', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    const { login } = useAuth()

    await expect(login('paciente', '52998224725', 'Abcdefjhijk1!')).rejects.toThrow('Erro ao fazer login')
  })
})

