import re
from typing import List

# --- Name Validation ---
def validate_name(name: str) -> List[str]:
    errors = []

    if not name:
        errors.append("Name is required.")
        return errors

    name = name.strip()

    if len(name) > 150:
        errors.append("Name must contain a maximum of 150 characters.")

    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ]+( [A-Za-zÀ-ÖØ-öø-ÿ]+)*", name):
        errors.append(
            "Name must contain only letters and single spaces between words."
        )

    return errors

# --- Password Complexity Validation ---
def check_password_complexity(password: str) -> List[str]:
    """Checks the password and returns a list of failed rules."""
    errors = []

    if len(password) > 255:
        errors.append("The password must contain a maximum of 255 characters.")

    if len(password) < 12:
        errors.append("Password must contain at least 12 characters.")

    if re.search(r'\s', password):
        errors.append("Password must not contain spaces.")

    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter.")

    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter.")

    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit.")

    if not re.search(r'[!@#$%^&*()_+={}\[\]|\\:;"\'<>,.?/~`]', password):
        errors.append("Password must contain at least one special character.")

    return errors

# --- Valid CPF verification ---
def validate_cpf(cpf: str) -> List[str]:
    errors = []

    if not cpf:
        errors.append("CPF is required.")
        return errors

    cpf = cpf.strip()

    if not cpf.isdigit():
        errors.append("CPF must contain only digits.")
        return errors

    if len(cpf) != 11:
        errors.append("CPF must contain exactly 11 digits.")
        return errors

    if cpf == cpf[0] * 11:
        errors.append("Invalid CPF.")
        return errors

    def calc_digit(seq: str, factor: int) -> int:
        total = sum(int(d) * (factor - i) for i, d in enumerate(seq))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    if int(cpf[9]) != calc_digit(cpf[:9], 10):
        errors.append("Invalid CPF.")
        return errors

    if int(cpf[10]) != calc_digit(cpf[:10], 11):
        errors.append("Invalid CPF.")

    return errors

# --- Valid CRM verification ---
def validate_crm(crm: str) -> List[str]:
    errors = []

    if not crm:
        errors.append("CRM is required.")
        return errors

    crm = crm.strip().upper()

    if len(crm) != 8:
        errors.append("CRM must be exactly 8 characters.")
        return errors

    if not re.fullmatch(r"[A-Z]{2}\d{6}", crm):
        errors.append("Invalid CRM format. Expected format: SP123456.")
        return errors

    return errors
