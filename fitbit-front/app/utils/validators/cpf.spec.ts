import { describe, it, expect } from 'vitest'
import { isValidCPF } from './cpf'

describe('isValidCPF', () => {
  describe('Valid CPFs - should return true', () => {
    it('should validate multiple correct CPFs', () => {
      const validCPFs = [
        '111.444.777-35',
        '11144477735',
        '529.982.247-25',
        '52998224725',
        '123.456.789-09',
        '12345678909'
      ]
      validCPFs.forEach(cpf => {
        expect(isValidCPF(cpf)).toBe(true)
      })
    })

    it('should handle CPF with different formatting patterns', () => {
      expect(isValidCPF('111.444.777-35')).toBe(true)
      expect(isValidCPF('111-444-777-35')).toBe(true)
      expect(isValidCPF('111 444 777 35')).toBe(true)
    })
  })

  describe('Invalid CPFs - should return false', () => {
    describe('Length validation', () => {
      it('should reject CPF shorter than 11 digits', () => {
        const shortCPFs = ['', '1', '12', '123', '1234567890']
        shortCPFs.forEach(cpf => {
          expect(isValidCPF(cpf)).toBe(false)
        })
      })

      it('should reject CPF longer than 11 digits', () => {
        const longCPFs = ['123456789012', '1234567890123', '111.444.777-355']
        longCPFs.forEach(cpf => {
          expect(isValidCPF(cpf)).toBe(false)
        })
      })
    })

    describe('Same digit sequences', () => {
      it('should reject all possible same-digit CPFs', () => {
        const sameDigitCPFs = [
          '00000000000', '11111111111', '22222222222', '33333333333',
          '44444444444', '55555555555', '66666666666', '77777777777',
          '88888888888', '99999999999'
        ]
        sameDigitCPFs.forEach(cpf => {
          expect(isValidCPF(cpf)).toBe(false)
        })
      })
    })

    describe('Check digit validation', () => {
      it('should reject CPF with wrong first check digit', () => {
        expect(isValidCPF('111.444.777-05')).toBe(false) // should be 35
        expect(isValidCPF('529.982.247-15')).toBe(false) // should be 25
      })

      it('should reject CPF with wrong second check digit', () => {
        expect(isValidCPF('111.444.777-34')).toBe(false) // should be 35
        expect(isValidCPF('529.982.247-24')).toBe(false) // should be 25
      })

      it('should reject CPF with both check digits wrong', () => {
        expect(isValidCPF('12345678901')).toBe(false)
        expect(isValidCPF('111.444.777-00')).toBe(false)
      })

      it('should reject CPF where digits are off by 1', () => {
        expect(isValidCPF('111.444.777-36')).toBe(false) // 35 + 1
        expect(isValidCPF('529.982.247-26')).toBe(false) // 25 + 1
      })
    })
  })

  describe('Edge cases', () => {
    it('should handle empty string', () => {
      expect(isValidCPF('')).toBe(false)
    })

    it('should handle string with only formatting characters', () => {
      expect(isValidCPF('...-')).toBe(false)
      expect(isValidCPF('   ')).toBe(false)
    })

    it('should handle CPF with letters', () => {
      expect(isValidCPF('111.444.777-3A')).toBe(false)
      expect(isValidCPF('ABC.DEF.GHI-JK')).toBe(false)
    })

    it('should strip special characters and validate remaining digits', () => {
      expect(isValidCPF('111@444#777$35')).toBe(true)
      expect(isValidCPF('111!444!777!35')).toBe(true)
    })
  })
})
