import { describe, it, expect } from 'vitest'
import { crmSchema } from './crm.schema'

describe('crmSchema', () => {
  describe('Valid CRMs - should pass', () => {
    it('should accept CRM with all valid Brazilian states', () => {
      const validStates = ['SP', 'RJ', 'MG', 'BA', 'RS', 'PR', 'PE', 'CE', 'PA', 'SC']
      validStates.forEach(state => {
        expect(crmSchema.safeParse(`${state}123456`).success).toBe(true)
      })
    })

    it('should accept CRM with exactly 8 characters (2 letters + 6 digits)', () => {
      expect(crmSchema.safeParse('SP123456').success).toBe(true)
      expect(crmSchema.safeParse('RJ000000').success).toBe(true)
      expect(crmSchema.safeParse('MG999999').success).toBe(true)
    })

    it('should transform to uppercase', () => {
      const testCases = [
        { input: 'sp123456', expected: 'SP123456' },
        { input: 'rj654321', expected: 'RJ654321' },
        { input: 'Mg123456', expected: 'MG123456' }
      ]
      testCases.forEach(({ input, expected }) => {
        const result = crmSchema.safeParse(input)
        expect(result.success).toBe(true)
        if (result.success) {
          expect(result.data).toBe(expected)
        }
      })
    })

    it('should trim whitespace', () => {
      const result = crmSchema.safeParse('  SP123456  ')
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data).toBe('SP123456')
      }
    })
  })

  describe('Invalid CRMs - should fail', () => {
    describe('Wrong format', () => {
      it('should reject CRM with less than 8 characters', () => {
        const tooShort = ['SP12345', 'RJ1234', 'MG123']
        tooShort.forEach(crm => {
          expect(crmSchema.safeParse(crm).success).toBe(false)
        })
      })

      it('should reject CRM with more than 8 characters', () => {
        const tooLong = ['SP1234567', 'RJ12345678']
        tooLong.forEach(crm => {
          expect(crmSchema.safeParse(crm).success).toBe(false)
        })
      })

      it('should reject CRM with wrong order (digits before letters)', () => {
        expect(crmSchema.safeParse('123456SP').success).toBe(false)
        expect(crmSchema.safeParse('123456/SP').success).toBe(false)
      })

      it('should reject CRM with only 1 letter', () => {
        expect(crmSchema.safeParse('S123456').success).toBe(false)
        expect(crmSchema.safeParse('R1234567').success).toBe(false)
      })

      it('should reject CRM with 3+ letters', () => {
        expect(crmSchema.safeParse('SPP123456').success).toBe(false)
        expect(crmSchema.safeParse('RJA123456').success).toBe(false)
      })

      it('should reject CRM with less than 6 digits', () => {
        expect(crmSchema.safeParse('SP12345').success).toBe(false)
        expect(crmSchema.safeParse('RJ1234').success).toBe(false)
      })

      it('should reject CRM with more than 6 digits', () => {
        expect(crmSchema.safeParse('SP1234567').success).toBe(false)
      })

      it('should reject CRM with letters in digit part', () => {
        expect(crmSchema.safeParse('SP12345A').success).toBe(false)
        expect(crmSchema.safeParse('RJA23456').success).toBe(false)
      })

      it('should reject CRM with numbers in state part', () => {
        expect(crmSchema.safeParse('S1123456').success).toBe(false)
        expect(crmSchema.safeParse('1P123456').success).toBe(false)
      })

      it('should reject CRM with special characters', () => {
        expect(crmSchema.safeParse('SP/123456').success).toBe(false)
        expect(crmSchema.safeParse('SP-123456').success).toBe(false)
        expect(crmSchema.safeParse('SP 123456').success).toBe(false)
      })
    })

    describe('Empty and invalid inputs', () => {
      it('should reject empty string', () => {
        const result = crmSchema.safeParse('')
        expect(result.success).toBe(false)
        if (!result.success) {
          expect(result.error.errors[0]?.message).toContain('required')
        }
      })

      it('should reject whitespace-only string', () => {
        expect(crmSchema.safeParse('   ').success).toBe(false)
      })
    })
  })
})
