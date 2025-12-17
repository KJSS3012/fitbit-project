import re
from typing import List

# --- Name Validation ---
def validate_name(name: str) -> str | None:
    
    if not name or not name.strip():
        return "Name is required or cannot be empty."
    
    name_stripped = name.strip()

    if name != name_stripped:
        return "Name cannot have leading or trailing spaces."

    elif len(name_stripped) > 150:
        return "Name must contain a maximum of 150 characters."

    elif not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ]+( [A-Za-zÀ-ÖØ-öø-ÿ]+)*", name_stripped):
        return "Name must contain only letters and single spaces between words."

    return None

# --- Password Complexity Validation ---
def check_password_complexity(password: str) -> str | None:
    """Checks the password and returns the first failed rule or None."""
    
    if len(password) > 255:
        return "The password must contain a maximum of 255 characters."

    elif len(password) < 12:
        return "Password must contain at least 12 characters."

    elif re.search(r'\s', password):
        return "Password must not contain spaces."

    elif not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter."

    elif not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter."

    elif not re.search(r'\d', password):
        return "Password must contain at least one digit."

    elif not re.search(r'[!@#$%^&*()_+={}\[\]|\\:;"\'<>,.?/~`]', password):
        return "Password must contain at least one special character."

    return None

# --- Valid CPF verification ---
def validate_cpf(cpf: str) -> str | None:
    
    cpf = cpf.strip()

    if not cpf:
        return "CPF is required."

    elif not cpf.isdigit():
        return "CPF must contain only digits."

    elif len(cpf) != 11:
        return "CPF must contain exactly 11 digits."

    elif cpf == cpf[0] * 11:
        return "Invalid CPF."
    
    def calc_digit(seq: str, factor: int) -> int:
        total = sum(int(d) * (factor - i) for i, d in enumerate(seq))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    if int(cpf[9]) != calc_digit(cpf[:9], 10):
        return "Invalid CPF."

    elif int(cpf[10]) != calc_digit(cpf[:10], 11):
        return "Invalid CPF."

    return None

# --- Valid CRM verification ---
def validate_crm(crm: str) -> str | None:

    crm = crm.strip().upper()

    if not crm:
        return "CRM is required."

    elif len(crm) != 8:
        return "CRM must be exactly 8 characters (2 letters + 6 digits)."

    elif not re.fullmatch(r"[A-Z]{2}\d{6}", crm):
        return "Invalid CRM format. Expected format: SP123456 (2 letters for state and 6 digits)."

    return None