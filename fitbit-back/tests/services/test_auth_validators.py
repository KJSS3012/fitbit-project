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
    assert validate_name("João Cabral") == []

def test_validate_name_empty():
    assert validate_name("") != []

def test_validate_name_only_spaces():
    assert validate_name("   ") != []

def test_validate_name_with_numbers():
    assert validate_name("João123") != []

def test_validate_name_with_special_chars():
    assert validate_name("João@Cabral") != []

def test_validate_name_multiple_spaces_inside():
    assert validate_name("João     Cabral") != []

def test_validate_name_trailing_space():
    assert validate_name("João Cabral ") != []


# -------------------
# CPF
# -------------------

def test_validate_cpf_valid():
    assert validate_cpf("52998224725") == []

def test_validate_cpf_invalid_length():
    assert validate_cpf("123") != []

def test_validate_cpf_letters():
    assert validate_cpf("abc98224725") != []

def test_validate_cpf_all_equal_digits():
    assert validate_cpf("11111111111") != []

def test_validate_cpf_invalid_digit():
    assert validate_cpf("52998224724") != []


# -------------------
# CRM
# -------------------

def test_validate_crm_upper_valid():
    assert validate_crm("SP123456") == []

def test_validate_crm_lowercase_valid():
    assert validate_crm("sp123456") == []

def test_validate_crm_mixed_valid():
    assert validate_crm("sP123456") == []

def test_validate_crm_wrong_length():
    assert validate_crm("SP123") != []

def test_validate_crm_invalid_format():
    assert validate_crm("12345678") != []

def test_validate_crm_letters_only():
    assert validate_crm("ABCDEFGH") != []


# -------------------
# PASSWORD
# -------------------

def test_password_valid():
    assert check_password_complexity("Abcdefghijk1!") == []

def test_password_too_short():
    assert check_password_complexity("A1!") != []

def test_password_no_uppercase():
    assert check_password_complexity("abcdefghijk1!") != []

def test_password_no_lowercase():
    assert check_password_complexity("ABCDEFGHIJK1!") != []

def test_password_no_number():
    assert check_password_complexity("Abcdefghijk!") != []

def test_password_no_special_char():
    assert check_password_complexity("Abcdefghijk1") != []