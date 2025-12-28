import { z } from 'zod'

export const crmSchema = z
  .string({ message: 'CRM is required' })
  .min(1, 'CRM is required')
  .trim()
  .toUpperCase()
  .regex(/^\d{4,6}$/, {
    message: 'CRM must contain 4 to 6 digits'
  })
