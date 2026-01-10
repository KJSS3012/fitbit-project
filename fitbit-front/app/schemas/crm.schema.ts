import { z } from 'zod'

export const crmSchema = z
  .string({ message: 'CRM is required' })
  .min(1, 'CRM is required')
  .trim()
  .toUpperCase()
  .regex(/^[A-Z]{2}\d{6}$/, {
    message: 'CRM must be exactly 8 characters (2 letters for state and 6 digits, e.g., SP123456)'
  })
