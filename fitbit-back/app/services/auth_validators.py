import re
from typing import List

# --- Name Validation ---
def validate_name(name: str) -> str | None:
    if not name or not name.strip():
        return "Nome é obrigatório"
    
    name_stripped = name.strip()

    if len(name_stripped) < 3:
        return "Nome deve conter no mínimo 3 caracteres"

    if name != name_stripped:
        return "Nome não pode ter espaços no início ou fim"

    elif len(name_stripped) > 150:
        return "Nome deve conter no máximo 150 caracteres"

    elif not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ]+( [A-Za-zÀ-ÖØ-öø-ÿ]+)*", name_stripped):
        return "Nome deve conter apenas letras e espaços simples entre palavras"

    return None

# --- Password Complexity Validation ---
def check_password_complexity(password: str) -> str | None:
    """Valida complexidade da senha e retorna primeira regra violada ou None."""
    if len(password) > 255:
        return "A senha deve conter no máximo 255 caracteres"

    elif len(password) < 12:
        return "Senha deve conter pelo menos 12 caracteres"

    elif re.search(r'\s', password):
        return "Senha não pode conter espaços"

    elif not re.search(r'[A-Z]', password):
        return "Senha deve conter pelo menos uma letra maiúscula"

    elif not re.search(r'[a-z]', password):
        return "Senha deve conter pelo menos uma letra minúscula"

    elif not re.search(r'\d', password):
        return "Senha deve conter pelo menos um número"

    elif not re.search(r'[!@#$%^&*()_+={}\[\]|\\:;"\'<>,.?/~`]', password):
        return "Senha deve conter pelo menos um caractere especial"

    return None

# --- Valid CPF verification ---
def validate_cpf(cpf: str) -> str | None:
    cpf = cpf.strip()

    if not cpf:
        return "CPF é obrigatório"

    elif not cpf.isdigit():
        return "CPF deve conter apenas dígitos"

    elif len(cpf) != 11:
        return "CPF deve conter exatamente 11 dígitos"

    elif cpf == cpf[0] * 11:
        return "CPF inválido"
    
    def calc_digit(seq: str, factor: int) -> int:
        total = sum(int(d) * (factor - i) for i, d in enumerate(seq))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    if int(cpf[9]) != calc_digit(cpf[:9], 10):
        return "CPF inválido"

    elif int(cpf[10]) != calc_digit(cpf[:10], 11):
        return "CPF inválido"

    return None

# --- Valid CRM verification ---
def validate_crm(crm: str) -> str | None:
    VALID_UFS = {
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT",
        "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO",
        "RR", "SC", "SP", "SE", "TO"
    }

    crm = crm.strip().upper()

    if not crm:
        return "CRM é obrigatório"

    elif len(crm) != 8:
        return "CRM deve ter exatamente 8 caracteres (2 letras + 6 dígitos)"

    elif not re.fullmatch(r"[A-Z]{2}\d{6}", crm):
        return "Formato de CRM inválido. Formato esperado: SP123456 (2 letras do estado e 6 dígitos)"

    acronym = crm[:2]
    if acronym not in VALID_UFS:
        return f"A sigla do estado '{acronym}' não é válida"

    return None