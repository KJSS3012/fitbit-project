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
    assert validate_name("") == "Nome é obrigatório"

def test_validate_name_whitespace_only():
    assert validate_name("   ") == "Nome é obrigatório"

def test_validate_name_leading_trailing_space():
    assert validate_name(" João Cabral") == "Nome não pode ter espaços no início ou fim"
    assert validate_name("João Cabral ") == "Nome não pode ter espaços no início ou fim"

def test_validate_name_too_long():
    long_name = "a" * 151
    assert validate_name(long_name) == "Nome deve conter no máximo 150 caracteres"

def test_validate_name_with_numbers():
    assert validate_name("João123") == "Nome deve conter apenas letras e espaços simples entre palavras"

def test_validate_name_with_special_chars():
    assert validate_name("João@Cabral") == "Nome deve conter apenas letras e espaços simples entre palavras"

def test_validate_name_multiple_spaces_inside():
    assert validate_name("João    Cabral") == "Nome deve conter apenas letras e espaços simples entre palavras"


# -------------------
# CPF
# -------------------

def test_validate_cpf_valid():
    assert validate_cpf("52998224725") is None

def test_validate_cpf_empty():
    assert validate_cpf("") == "CPF é obrigatório"

def test_validate_cpf_non_digits():
    assert validate_cpf("abc98224725") == "CPF deve conter apenas dígitos"

def test_validate_cpf_invalid_length():
    assert validate_cpf("123") == "CPF deve conter exatamente 11 dígitos"

def test_validate_cpf_all_equal_digits():
    assert validate_cpf("11111111111") == "CPF inválido"

def test_validate_cpf_invalid_check_digit():
    assert validate_cpf("52998224724") == "CPF inválido"


# -------------------
# CRM
# -------------------

def test_validate_crm_valid_uppercase():
    assert validate_crm("SP123456") is None

def test_validate_crm_valid_lowercase():
    assert validate_crm("sp123456") is None

def test_validate_crm_empty():
    assert validate_crm("") == "CRM é obrigatório"

def test_validate_crm_wrong_length():
    assert validate_crm("SP123") == "CRM deve ter exatamente 8 caracteres (2 letras + 6 dígitos)"

def test_validate_crm_invalid_format():
    assert validate_crm("12345678") == "Formato de CRM inválido. Formato esperado: SP123456 (2 letras do estado e 6 dígitos)"
    assert validate_crm("ABCDEFGH") == "Formato de CRM inválido. Formato esperado: SP123456 (2 letras do estado e 6 dígitos)"

def test_validate_crm_invalid_uf():
    assert validate_crm("XX123456") == "A sigla do estado 'XX' não é válida"


# -------------------
# PASSWORD
# -------------------

def test_password_valid():
    assert check_password_complexity("Abcdefghijk1!") is None

def test_password_too_long():
    long_pass = "A" * 256
    assert check_password_complexity(long_pass) == "A senha deve conter no máximo 255 caracteres"

def test_password_too_short():
    assert check_password_complexity("A1!") == "Senha deve conter pelo menos 12 caracteres"

def test_password_contains_space():
    assert check_password_complexity("Abc defghijk1!") == "Senha não pode conter espaços"

def test_password_no_uppercase():
    assert check_password_complexity("abcdefghijk1!") == "Senha deve conter pelo menos uma letra maiúscula"

def test_password_no_lowercase():
    assert check_password_complexity("ABCDEFGHIJK1!") == "Senha deve conter pelo menos uma letra minúscula"

def test_password_no_digit():
    assert check_password_complexity("Abcdefghijk!") == "Senha deve conter pelo menos um número"

def test_password_no_special_char():
    assert check_password_complexity("Abcdefghijk1") == "Senha deve conter pelo menos um caractere especial"