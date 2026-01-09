import pytest
from app.services.auth_validators import (
    validate_name,
    validate_cpf,
    validate_crm,
    check_password_complexity,
)

# -------------------
# NAME
# -------------------

def test_validate_name_valid():
    assert validate_name("João Cabral") is None

def test_validate_name_empty():
    assert validate_name("") == "Name is required or cannot be empty."

def test_validate_name_whitespace_only():
    assert validate_name("   ") == "Name is required or cannot be empty."

def test_validate_name_leading_trailing_space():
    assert validate_name(" João Cabral") == "Name cannot have leading or trailing spaces."
    assert validate_name("João Cabral ") == "Name cannot have leading or trailing spaces."

def test_validate_name_too_long():
    long_name = "a" * 151
    assert validate_name(long_name) == "Name must contain a maximum of 150 characters."

def test_validate_name_with_numbers():
    assert validate_name("João123") == "Name must contain only letters and single spaces between words."

def test_validate_name_with_special_chars():
    assert validate_name("João@Cabral") == "Name must contain only letters and single spaces between words."

def test_validate_name_multiple_spaces_inside():
    assert validate_name("João    Cabral") == "Name must contain only letters and single spaces between words."


# -------------------
# CPF
# -------------------

def test_validate_cpf_valid():
    assert validate_cpf("52998224725") is None

def test_validate_cpf_empty():
    assert validate_cpf("") == "CPF is required."

def test_validate_cpf_non_digits():
    assert validate_cpf("abc98224725") == "CPF must contain only digits."

def test_validate_cpf_invalid_length():
    assert validate_cpf("123") == "CPF must contain exactly 11 digits."

def test_validate_cpf_all_equal_digits():
    assert validate_cpf("11111111111") == "Invalid CPF."

def test_validate_cpf_invalid_check_digit():
    assert validate_cpf("52998224724") == "Invalid CPF."


# -------------------
# CRM
# -------------------

def test_validate_crm_valid_uppercase():
    assert validate_crm("SP123456") is None

def test_validate_crm_valid_lowercase():
    assert validate_crm("sp123456") is None

def test_validate_crm_empty():
    assert validate_crm("") == "CRM is required."

def test_validate_crm_wrong_length():
    assert validate_crm("SP123") == "CRM must be exactly 8 characters (2 letters + 6 digits)."

def test_validate_crm_invalid_format():
    assert validate_crm("12345678") == "Invalid CRM format. Expected format: SP123456 (2 letters for state and 6 digits)."
    assert validate_crm("ABCDEFGH") == "Invalid CRM format. Expected format: SP123456 (2 letters for state and 6 digits)."

def test_validate_crm_invalid_uf():
    assert validate_crm("XX123456") == "The state acronym 'XX' is not valid."


# -------------------
# PASSWORD
# -------------------

def test_password_valid():
    assert check_password_complexity("Abcdefghijk1!") is None

def test_password_too_long():
    long_pass = "A" * 256
    assert check_password_complexity(long_pass) == "The password must contain a maximum of 255 characters."

def test_password_too_short():
    assert check_password_complexity("A1!") == "Password must contain at least 12 characters."

def test_password_contains_space():
    assert check_password_complexity("Abc defghijk1!") == "Password must not contain spaces."

def test_password_no_uppercase():
    assert check_password_complexity("abcdefghijk1!") == "Password must contain at least one uppercase letter."

def test_password_no_lowercase():
    assert check_password_complexity("ABCDEFGHIJK1!") == "Password must contain at least one lowercase letter."

def test_password_no_digit():
    assert check_password_complexity("Abcdefghijk!") == "Password must contain at least one digit."

def test_password_no_special_char():
    assert check_password_complexity("Abcdefghijk1") == "Password must contain at least one special character."