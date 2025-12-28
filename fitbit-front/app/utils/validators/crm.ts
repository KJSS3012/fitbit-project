const CRM_REGEX = /^\d{4,6}(\/[A-Z]{2})?$/

export function isValidCRM(crm?: string): boolean {
  if (!crm) return false
  return CRM_REGEX.test(crm.trim().toUpperCase())
}
