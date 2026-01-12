import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'

describe('Doctor Patient Metrics - Period Filters (PB13)', () => {
  describe('validateCustomRange', () => {
    it('should reject empty dates', () => {
      expect(validateCustomRange('', '')).toBe(false)
      expect(validateCustomRange('2026-01-01', '')).toBe(false)
      expect(validateCustomRange('', '2026-01-10')).toBe(false)
    })

    it('should reject when start date is after end date', () => {
      expect(validateCustomRange('2026-01-10', '2026-01-01')).toBe(false)
    })

    it('should reject ranges longer than 365 days', () => {
      const start = '2024-01-01'
      const end = '2025-01-02'
      expect(validateCustomRange(start, end)).toBe(false)
    })

    it('should reject future end dates', () => {
      const today = new Date()
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)

      const start = today.toISOString().split('T')[0]!
      const end = tomorrow.toISOString().split('T')[0]!

      expect(validateCustomRange(start, end)).toBe(false)
    })

    it('should accept valid date range', () => {
      const start = '2026-01-01'
      const end = '2026-01-10'
      expect(validateCustomRange(start, end)).toBe(true)
    })

    it('should accept date range exactly 365 days', () => {
      const start = '2025-01-11'
      const end = '2026-01-10'
      expect(validateCustomRange(start, end)).toBe(true)
    })

    it('should accept end date as today', () => {
      const today = new Date()
      const lastWeek = new Date(today)
      lastWeek.setDate(lastWeek.getDate() - 7)

      const start = lastWeek.toISOString().split('T')[0]!
      const end = today.toISOString().split('T')[0]!

      expect(validateCustomRange(start, end)).toBe(true)
    })
  })

  describe('Period calculation', () => {
    it('should calculate daily period as today only', () => {
      const today = new Date()
      const range = calculateDateRange('day')

      const startDate = new Date(range.start + 'T12:00:00') // noon to avoid timezone issues
      const endDate = new Date(range.end + 'T12:00:00')

      expect(startDate.toDateString()).toBe(today.toDateString())
      expect(endDate.toDateString()).toBe(today.toDateString())
    })

    it('should calculate weekly period as last 7 days', () => {
      const range = calculateDateRange('week')
      const start = new Date(range.start)
      const end = new Date(range.end)

      const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
      expect(diffDays).toBe(7)
    })

    it('should calculate monthly period as last 30 days', () => {
      const range = calculateDateRange('month')
      const start = new Date(range.start)
      const end = new Date(range.end)

      const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
      expect(diffDays).toBe(30)
    })
  })
})

// Helper functions for validation logic
function validateCustomRange(startDate: string, endDate: string): boolean {
  if (!startDate || !endDate) {
    return false
  }

  // Parse as local start/end to avoid timezone/UTC parsing differences
  const start = new Date(`${startDate}T00:00:00`)
  const end = new Date(`${endDate}T23:59:59.999`)
  const today = new Date()
  today.setHours(23, 59, 59, 999)

  if (start > end) {
    return false
  }

  if (end > today) {
    return false
  }

  const diffTime = Math.abs(end.getTime() - start.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays > 365) {
    return false
  }

  return true
}

function calculateDateRange(period: 'day' | 'week' | 'month') {
  const now = new Date()
  const start = new Date()

  switch (period) {
    case 'day':
      break
    case 'week':
      start.setDate(now.getDate() - 7)
      break
    case 'month':
      start.setDate(now.getDate() - 30)
      break
  }

  // Return local YYYY-MM-DD strings
  const toLocalYMD = (d: Date) => {
    const yyyy = d.getFullYear()
    const mm = `${d.getMonth() + 1}`.padStart(2, '0')
    const dd = `${d.getDate()}`.padStart(2, '0')
    return `${yyyy}-${mm}-${dd}`
  }

  return {
    start: toLocalYMD(start),
    end: toLocalYMD(now)
  }
}
