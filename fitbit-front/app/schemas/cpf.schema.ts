import { z } from 'zod'

export function isValidCPF(cpf: string): boolean {
  const clean = cpf.replace(/\D/g, '')

  if (clean.length !== 11) return false
  if (/^(\d)\1+$/.test(clean)) return false

  let sum = 0
  for (let i = 0; i < 9; i++) {
    sum += Number(clean[i]) * (10 - i)
  }
  let check1 = (sum * 10) % 11
  if (check1 === 10) check1 = 0
  if (check1 !== Number(clean[9])) return false

  sum = 0
  for (let i = 0; i < 10; i++) {
    sum += Number(clean[i]) * (11 - i)
  }
  let check2 = (sum * 10) % 11
  if (check2 === 10) check2 = 0
  if (check2 !== Number(clean[10])) return false

  return true
}

export const cpfSchema = z
  .string({ message: 'CPF is required' })
  .min(1, 'CPF is required')
  .transform(v => v.replace(/\D/g, ''))
  .refine(isValidCPF, {
    message: 'Please enter a valid CPF'
  })
