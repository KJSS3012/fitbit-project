import { z } from 'zod'
import { cpfSchema } from './cpf.schema'
import { crmSchema } from './crm.schema'

/* -------------------- */
/* REGISTER */
/* -------------------- */
export const registerSchema = z.object({
  userType: z.enum(['paciente', 'medico']),
  name: z
    .string({ message: 'Full name is required' })
    .min(1, 'Full name is required')
    .min(3, 'Full name must be at least 3 characters'),
  cpf: cpfSchema,

  crm: z.string().optional(),

  password: z
    .string({ message: 'Password is required' })
    .min(1, 'Password is required')
    .min(12, 'Password must be at least 12 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),

  confirmPassword: z
    .string({ message: 'Please confirm your password' })
    .min(1, 'Please confirm your password'),

  acceptTerms: z
    .boolean()
    .refine(val => val === true, {
      message: 'You must accept the terms of use'
    })
}).superRefine((data, ctx) => {
  if (data.userType === 'medico') {
    if (!data.crm || data.crm.trim() === '') {
      ctx.addIssue({
        path: ['crm'],
        message: 'CRM is required for doctors',
        code: z.ZodIssueCode.custom
      })
    } else {
      // Validate CRM format
      const crmTrimmed = data.crm.trim().toUpperCase()
      if (!/^\d{4,6}$/.test(crmTrimmed)) {
        ctx.addIssue({
          path: ['crm'],
          message: 'CRM must contain 4 to 6 digits',
          code: z.ZodIssueCode.custom
        })
      }
    }
  }

  if (data.password !== data.confirmPassword) {
    ctx.addIssue({
      path: ['confirmPassword'],
      message: 'Passwords do not match',
      code: z.ZodIssueCode.custom
    })
  }
})

/* -------------------- */
/* LOGIN */
/* -------------------- */
export const loginSchema = z.object({
  userType: z.enum(['paciente', 'medico']),
  cpf: z.string().optional(),
  crm: z.string().optional(),
  password: z
    .string({ message: 'Password is required' })
    .min(1, 'Password is required'),
  rememberMe: z.boolean().optional()
}).superRefine((data, ctx) => {
  if (data.userType === 'paciente') {
    if (!data.cpf) {
      ctx.addIssue({
        path: ['cpf'],
        message: 'CPF is required',
        code: z.ZodIssueCode.custom
      })
    } else {
      const clean = data.cpf.replace(/\D/g, '')
      const cpfResult = cpfSchema.safeParse(data.cpf)
      if (!cpfResult.success) {
        ctx.addIssue({
          path: ['cpf'],
          message: 'Invalid CPF',
          code: z.ZodIssueCode.custom
        })
      }
    }
  }

  if (data.userType === 'medico') {
    if (!data.crm) {
      ctx.addIssue({
        path: ['crm'],
        message: 'CRM is required',
        code: z.ZodIssueCode.custom
      })
    } else {
      const crmResult = crmSchema.safeParse(data.crm)
      if (!crmResult.success) {
        ctx.addIssue({
          path: ['crm'],
          message: 'Invalid CRM',
          code: z.ZodIssueCode.custom
        })
      }
    }
  }
})
