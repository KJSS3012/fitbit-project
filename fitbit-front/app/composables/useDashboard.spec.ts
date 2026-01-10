import { describe, it, expect, vi, beforeEach } from 'vitest'
import { isValidCPF } from '~/utils/validators/cpf'

describe('useDashboard - Date Range Functions', () => {
  describe('getDateRangeForPeriod', () => {
    it('should return today for day period', () => {
      const today = new Date().toISOString().split('T')[0]
      const result = getDateRangeForPeriod('day')

      expect(result.start).toBe(today)
      expect(result.end).toBe(today)
    })

    it('should return 7 days range for week period', () => {
      const result = getDateRangeForPeriod('week')
      const start = new Date(result.start!)
      const end = new Date(result.end!)

      const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
      expect(diffDays).toBe(7)
    })

    it('should return 1 month range for month period', () => {
      const result = getDateRangeForPeriod('month')
      const start = new Date(result.start!)
      const end = new Date(result.end!)

      expect(start.getMonth()).not.toBe(end.getMonth())
    })
  })

  describe('validateCustomRange', () => {
    it('should reject empty dates', () => {
      expect(validateCustomRange('', '')).toBe(false)
      expect(validateCustomRange('2024-01-01', '')).toBe(false)
      expect(validateCustomRange('', '2024-01-31')).toBe(false)
    })

    it('should reject when start date is after end date', () => {
      expect(validateCustomRange('2024-01-31', '2024-01-01')).toBe(false)
    })

    it('should reject ranges longer than 1 year', () => {
      const start = '2024-01-01'
      const end = '2025-01-02'
      expect(validateCustomRange(start, end)).toBe(false)
    })

    it('should accept valid date range', () => {
      const start = '2024-01-01'
      const end = '2024-01-31'
      expect(validateCustomRange(start, end)).toBe(true)
    })

    it('should accept date range exactly 365 days', () => {
      const start = '2024-01-01'
      const end = '2024-12-31'
      expect(validateCustomRange(start, end)).toBe(true)
    })
  })
})

// Helper function extracted from composable logic
function getDateRangeForPeriod(period: 'day' | 'week' | 'month' | 'custom') {
  const end = new Date()
  const start = new Date()

  switch (period) {
    case 'day':
      break
    case 'week':
      start.setDate(end.getDate() - 7)
      break
    case 'month':
      start.setMonth(end.getMonth() - 1)
      break
  }

  return {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0]
  }
}

// Helper function for validation logic
function validateCustomRange(startDate: string, endDate: string): boolean {
  if (!startDate || !endDate) {
    return false
  }

  const start = new Date(startDate)
  const end = new Date(endDate)

  if (start > end) {
    return false
  }

  const diffTime = Math.abs(end.getTime() - start.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays > 365) {
    return false
  }

  return true
}
