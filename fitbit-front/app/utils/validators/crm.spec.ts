import { describe, it, expect } from 'vitest'
import { isValidCRM } from './crm'

describe('isValidCRM', () => {
  describe('Valid CRMs - should return true', () => {
    it('should validate CRM with all valid Brazilian states', () => {
      const states = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
      states.forEach(state => {
        expect(isValidCRM(`${state}123456`)).toBe(true)
        expect(isValidCRM(`${state}000000`)).toBe(true)
        expect(isValidCRM(`${state}999999`)).toBe(true)
      })
    })

    it('should handle case insensitive state codes', () => {
      const variations = ['sp123456', 'Sp123456', 'sP123456', 'SP123456']
      variations.forEach(crm => {
        expect(isValidCRM(crm)).toBe(true)
      })
    })

    it('should handle whitespace around CRM', () => {
      expect(isValidCRM('  SP123456  ')).toBe(true)
      expect(isValidCRM('\tRJ654321\t')).toBe(true)
      expect(isValidCRM(' MG123456 ')).toBe(true)
    })

    it('should validate exact format (2 letters + 6 digits)', () => {
      expect(isValidCRM('SP123456')).toBe(true)
      expect(isValidCRM('RJ000000')).toBe(true)
      expect(isValidCRM('MG999999')).toBe(true)
    })
  })

  describe('Invalid CRMs - should return false', () => {
    describe('Format violations', () => {
      it('should reject CRM with wrong state code', () => {
        expect(isValidCRM('XX123456')).toBe(false)
        expect(isValidCRM('ZZ123456')).toBe(false)
        expect(isValidCRM('AB123456')).toBe(false)
      })

      it('should reject CRM with less than 8 characters', () => {
        const tooShort = ['SP12345', 'RJ1234', 'MG123']
        tooShort.forEach(crm => {
          expect(isValidCRM(crm)).toBe(false)
        })
      })

      it('should reject CRM with more than 8 characters', () => {
        const tooLong = ['SP1234567', 'RJ12345678', 'MG123456789']
        tooLong.forEach(crm => {
          expect(isValidCRM(crm)).toBe(false)
        })
      })

      it('should reject CRM with wrong order (digits before letters)', () => {
        expect(isValidCRM('123456SP')).toBe(false)
        expect(isValidCRM('654321RJ')).toBe(false)
      })

      it('should reject old format with slash', () => {
        expect(isValidCRM('123456/SP')).toBe(false)
        expect(isValidCRM('SP/123456')).toBe(false)
      })
    })

    describe('Invalid state format', () => {
      it('should reject with only 1 letter', () => {
        expect(isValidCRM('S123456')).toBe(false)
        expect(isValidCRM('R1234567')).toBe(false)
      })

      it('should reject with 3+ letters', () => {
        expect(isValidCRM('SPP123456')).toBe(false)
        expect(isValidCRM('RJA123456')).toBe(false)
      })

      it('should reject with numbers in state part', () => {
        expect(isValidCRM('S1123456')).toBe(false)
        expect(isValidCRM('1P123456')).toBe(false)
        expect(isValidCRM('12123456')).toBe(false)
      })
    })

    describe('Invalid digit part', () => {
      it('should reject with letters in number part', () => {
        expect(isValidCRM('SP12345A')).toBe(false)
        expect(isValidCRM('RJA23456')).toBe(false)
        expect(isValidCRM('MG12A456')).toBe(false)
      })

      it('should reject with less than 6 digits', () => {
        expect(isValidCRM('SP12345')).toBe(false)
        expect(isValidCRM('RJ1234')).toBe(false)
      })

      it('should reject with more than 6 digits', () => {
        expect(isValidCRM('SP1234567')).toBe(false)
      })
    })

    describe('Special characters and separators', () => {
      it('should reject with special characters', () => {
        expect(isValidCRM('SP@12345')).toBe(false)
        expect(isValidCRM('RJ#12345')).toBe(false)
        expect(isValidCRM('MG$12345')).toBe(false)
      })

      it('should reject with separators', () => {
        expect(isValidCRM('SP-123456')).toBe(false)
        expect(isValidCRM('SP 123456')).toBe(false)
        expect(isValidCRM('SP.123456')).toBe(false)
        expect(isValidCRM('')).toBe(false)
      })

      it('should reject undefined', () => {
        expect(isValidCRM()).toBe(false)
        expect(isValidCRM(undefined)).toBe(false)
      })

      it('should reject whitespace-only string', () => {
        expect(isValidCRM('   ')).toBe(false)
        expect(isValidCRM('\t')).toBe(false)
      })
    })
  })
})
