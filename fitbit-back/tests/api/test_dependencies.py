# tests/test_dependencies.py
import pytest
from fastapi import HTTPException
from jose import jwt
from app.api.dependencies import get_current_user_cpf
from app.core.settings import SETTINGS
from app.core.security import get_password_hash, verify_password, create_access_token


# --- Core Security Utilities: Hashing & Token Generation ---

def test_password_hashing():
    """
    Scenario: A plain password is hashed and verified.
    Expected Result: Verification returns True for the correct password and False for an incorrect one.
    """
    password = "my_secret_password"
    generated_hash = get_password_hash(password)
    
    assert generated_hash != password
    assert verify_password(password, generated_hash) is True
    assert verify_password("wrong_password", generated_hash) is False

def test_create_access_token():
    """
    Scenario: A JWT access token is generated with a subject and user type.
    Expected Result: The token contains the correct subject ('sub'), user type, and expiration claim.
    """
    cpf = "12345678900"
    token = create_access_token(subject=cpf, user_type="patient")
    
    payload = jwt.decode(token, SETTINGS["SECRET_KEY"], algorithms=[SETTINGS["ALGORITHM"]])
    
    assert payload["sub"] == cpf
    assert payload["type"] == "patient"
    assert "exp" in payload


# --- API Dependency: Token Validation & Data Extraction ---

def test_get_current_user_cpf_success():
    """
    Scenario: The token is valid and signed with our SECRET_KEY.
    Expected Result: The function must return the CPF ("sub").
    """
    test_cpf = "12345678900"
    payload = {"sub": test_cpf}
    
    # Manually generate a valid token using the same app settings
    valid_token = jwt.encode(payload, SETTINGS["SECRET_KEY"], algorithm=SETTINGS["ALGORITHM"])

    # Call the function directly (as if it were a standard function)
    result = get_current_user_cpf(token=valid_token)

    assert result == test_cpf

def test_get_current_user_cpf_invalid_token():
    """
    Scenario: The token is random text or signed with a different key.
    Expected Result: Should raise HTTPException 401 with specific detail.
    """
    invalid_token = "totally.wrong.token"

    with pytest.raises(HTTPException) as exc:
        get_current_user_cpf(token=invalid_token)
    
    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"

def test_get_current_user_cpf_missing_sub():
    """
    Scenario: The token is valid (signature ok), but missing the 'sub' field (CPF).
    Expected Result: Should raise HTTPException 401 with specific detail.
    """
    # Payload without the "sub" field
    payload = {"name": "Test Without CPF"} 
    token_missing_sub = jwt.encode(payload, SETTINGS["SECRET_KEY"], algorithm=SETTINGS["ALGORITHM"])

    with pytest.raises(HTTPException) as exc:
        get_current_user_cpf(token=token_missing_sub)
    
    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"