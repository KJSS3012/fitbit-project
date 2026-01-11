import pytest
from jose import jwt
from app.core.security import create_access_token, verify_password, get_password_hash, SECRET_KEY, ALGORITHM

def test_password_hashing_and_verification():
    """Verify that password hashing and verification work correctly."""
    password = "SafePassword123!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_pass", hashed) is False

def test_jwt_token_payload():
    """Verify that JWT tokens are created with correct payload."""
    cpf = "12345678900"
    user_type = "patient"
    token = create_access_token(subject=cpf, user_type=user_type)
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    assert payload["sub"] == cpf
    assert payload["type"] == user_type
    assert "exp" in payload