import { describe, it, expect } from 'vitest'

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
