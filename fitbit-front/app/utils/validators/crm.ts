const CRM_REGEX = /^[A-Z]{2}\d{6}$/

const VALID_UFS = new Set([
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT',
  'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO',
  'RR', 'SC', 'SP', 'SE', 'TO'
])

export function isValidCRM(crm?: string): boolean {
  if (!crm) return false
  const normalized = crm.trim().toUpperCase()
  if (!CRM_REGEX.test(normalized)) return false

  const uf = normalized.substring(0, 2)
  return VALID_UFS.has(uf)
}
