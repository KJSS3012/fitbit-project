from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.settings import SETTINGS 

security_scheme = HTTPBearer()

def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """Decodes and validates the token received in the Header."""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token, 
            SETTINGS["SECRET_KEY"], 
            algorithms=[SETTINGS["ALGORITHM"]]
        )
        return payload  # Returns data (cpf, type, etc) if valid
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Configure password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a hashed password from a plain password."""
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], user_type: str) -> str:
    """
    Create a JWT access token.
    user_type: "patient" or "doctor"
    """
    expire = datetime.utcnow() + timedelta(minutes=SETTINGS["ACCESS_TOKEN_EXPIRE_MINUTES"])
    
    to_encode = {
        "sub": str(subject),
        "type": user_type,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, SETTINGS["SECRET_KEY"], algorithm=SETTINGS["ALGORITHM"])
    return encoded_jwt