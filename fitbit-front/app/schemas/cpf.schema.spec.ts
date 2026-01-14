import { describe, it, expect } from 'vitest'
import { cpfSchema } from './cpf.schema'

describe('cpfSchema', () => {
  describe('Valid CPFs - should pass', () => {
    it('should accept valid CPF with formatting', () => {
      const result = cpfSchema.safeParse('111.444.777-35')
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data).toBe('11144477735')
      }
    })

    it('should accept valid CPF without formatting', () => {
      const result = cpfSchema.safeParse('11144477735')
      expect(result.success).toBe(true)
    })

    it('should accept multiple valid CPFs', () => {
      const validCPFs = [
        '529.982.247-25',
        '52998224725',
        '123.456.789-09',
        '12345678909'
      ]
      validCPFs.forEach(cpf => {
        expect(cpfSchema.safeParse(cpf).success).toBe(true)
      })
    })

    it('should strip all formatting characters', () => {
      const result = cpfSchema.safeParse('111.444.777-35')
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data).toBe('11144477735')
        expect(result.data).not.toContain('.')
        expect(result.data).not.toContain('-')
        expect(result.data.length).toBe(11)
      }
    })
  })

  describe('Invalid CPFs - should fail', () => {
    it('should reject CPF with wrong check digits', () => {
      const invalidCPFs = [
        '12345678901', // random invalid
        '111.444.777-36', // last digit wrong
        '111.444.777-25', // both check digits wrong
        '52998224726' // last digit off by 1
      ]
      invalidCPFs.forEach(cpf => {
        const result = cpfSchema.safeParse(cpf)
        expect(result.success).toBe(false)
        if (!result.success) {
          expect(result.error.errors[0]?.message).toContain('valid CPF')
        }
      })
    })

    it('should reject CPF with all same digits', () => {
      const samedigitCPFs = ['00000000000', '11111111111', '22222222222', '99999999999']
      samedigitCPFs.forEach(cpf => {
        expect(cpfSchema.safeParse(cpf).success).toBe(false)
      })
    })

    it('should reject empty or whitespace-only string', () => {
      const result = cpfSchema.safeParse('')
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.errors[0]?.message).toContain('required')
      }
    })
  })

  describe('Boundary and edge cases', () => {
    it('should reject CPF with less than 11 digits', () => {
      const shortCPFs = ['1', '12', '123', '1234567890']
      shortCPFs.forEach(cpf => {
        expect(cpfSchema.safeParse(cpf).success).toBe(false)
      })
    })

    it('should reject CPF with more than 11 digits', () => {
      const longCPFs = ['123456789012', '1234567890123', '12345678901234567890']
      longCPFs.forEach(cpf => {
        expect(cpfSchema.safeParse(cpf).success).toBe(false)
      })
    })

    it('should handle CPF with various formatting patterns', () => {
      const formattedCPF = '111-444-777-35'
      const result = cpfSchema.safeParse(formattedCPF)
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data).toBe('11144477735')
      }
    })

    it('should reject CPF with letters', () => {
      expect(cpfSchema.safeParse('111.444.777-3A').success).toBe(false)
      expect(cpfSchema.safeParse('ABC.DEF.GHI-JK').success).toBe(false)
    })

    it('should strip special characters and validate remaining digits', () => {
      const result = cpfSchema.safeParse('111@444#777$35')
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data).toBe('11144477735')
      }
    })
  })
})
