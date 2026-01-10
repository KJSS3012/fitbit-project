import { z } from 'zod'
import { cpfSchema } from './cpf.schema'
import { crmSchema } from './crm.schema'

/* -------------------- */
/* REGISTER */
/* -------------------- */
export const registerSchema = z.object({
  userType: z.enum(['paciente', 'medico']),
  name: z
    .string({ message: 'Nome completo é obrigatório' })
    .min(1, 'Nome completo é obrigatório')
    .min(3, 'Nome deve ter pelo menos 3 caracteres'),
  cpf: cpfSchema,

  crm: z.string().optional(),

  password: z
    .string({ message: 'Senha é obrigatória' })
    .min(1, 'Senha é obrigatória')
    .min(12, 'Senha deve ter pelo menos 12 caracteres')
    .regex(/[A-Z]/, 'Senha deve conter pelo menos uma letra maiúscula')
    .regex(/[a-z]/, 'Senha deve conter pelo menos uma letra minúscula')
    .regex(/[0-9]/, 'Senha deve conter pelo menos um número')
    .regex(/[^A-Za-z0-9]/, 'Senha deve conter pelo menos um caractere especial'),

  confirmPassword: z
    .string({ message: 'Por favor, confirme sua senha' })
    .min(1, 'Por favor, confirme sua senha'),

  acceptTerms: z
    .boolean()
    .refine(val => val === true, {
      message: 'Você deve aceitar os termos de uso'
    })
}).superRefine((data, ctx) => {
  if (data.userType === 'medico') {
    if (!data.crm || data.crm.trim() === '') {
      ctx.addIssue({
        path: ['crm'],
        message: 'CRM é obrigatório para médicos',
        code: z.ZodIssueCode.custom
      })
    } else {
      // Validate CRM format (2 letters + 6 digits, e.g., SP123456)
      const crmTrimmed = data.crm.trim().toUpperCase()
      if (!/^[A-Z]{2}\d{6}$/.test(crmTrimmed)) {
        ctx.addIssue({
          path: ['crm'],
          message: 'CRM deve ter exatamente 8 caracteres (2 letras do estado e 6 dígitos, ex: SP123456)',
          code: z.ZodIssueCode.custom
        })
      }
    }
  }

  if (data.password !== data.confirmPassword) {
    ctx.addIssue({
      path: ['confirmPassword'],
      message: 'As senhas não coincidem',
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
    .string({ message: 'Senha é obrigatória' })
    .min(1, 'Senha é obrigatória'),
  rememberMe: z.boolean().optional()
}).superRefine((data, ctx) => {
  if (data.userType === 'paciente') {
    if (!data.cpf) {
      ctx.addIssue({
        path: ['cpf'],
        message: 'CPF é obrigatório',
        code: z.ZodIssueCode.custom
      })
    } else {
      const clean = data.cpf.replace(/\D/g, '')
      const cpfResult = cpfSchema.safeParse(data.cpf)
      if (!cpfResult.success) {
        ctx.addIssue({
          path: ['cpf'],
          message: 'CPF inválido',
          code: z.ZodIssueCode.custom
        })
      }
    }
  }

  if (data.userType === 'medico') {
    if (!data.crm) {
      ctx.addIssue({
        path: ['crm'],
        message: 'CRM é obrigatório',
        code: z.ZodIssueCode.custom
      })
    } else {
      const crmResult = crmSchema.safeParse(data.crm)
      if (!crmResult.success) {
        ctx.addIssue({
          path: ['crm'],
          message: 'CRM inválido',
          code: z.ZodIssueCode.custom
        })
      }
    }
  }
})
