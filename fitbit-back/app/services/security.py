from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from passlib.context import CryptContext

# Security Configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
SECRET_KEY = "SUPER_SECRET_KEY_123"  # In production, hide this in env vars

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if the plain password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes the password."""
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], user_type: str) -> str:
    """
    Generates the JWT Token.
    subject: usually the Unique ID (CPF or CRM)
    user_type: 'patient' or 'doctor' (to identify role)
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload content
    to_encode = {
        "exp": expire, 
        "sub": str(subject),
        "type": user_type 
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt