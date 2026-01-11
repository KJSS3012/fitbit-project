import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from app.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    SECRET_KEY, 
    ALGORITHM,
    get_current_user_cpf
)

# --- Core Security Utilities ---

def test_password_hashing():
    password = "my_secret_password"
    generated_hash = get_password_hash(password)
    assert verify_password(password, generated_hash) is True

def test_create_access_token():
    cpf = "12345678900"
    token = create_access_token(subject=cpf, user_type="patient")
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    assert payload["sub"] == cpf
    assert payload["type"] == "patient"

from unittest.mock import patch

def test_get_current_user_cpf_success():
    """
    Scenario: The token is valid and the user exists.
    """
    test_cpf = "12345678900"
    from app.models.mock import FAKE_PATIENTS_DB
    
    if not any(p.get("cpf") == test_cpf for p in FAKE_PATIENTS_DB):
        FAKE_PATIENTS_DB.append({"cpf": test_cpf})

    token = create_access_token(subject=test_cpf, user_type="patient")
    mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with patch("app.core.security.load_persistence"):
        result = get_current_user_cpf(credentials=mock_creds)
    
    assert result == test_cpf