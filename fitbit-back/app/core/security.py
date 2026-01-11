import os
from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.mock import FAKE_PATIENTS_DB
from app.core.fitbit_client import load_persistence

# Settings manually defined to avoid import errors
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- PASSWORD LOGIC ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- TOKEN GENERATION ---
def create_access_token(subject: Union[str, Any], user_type: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(subject), "type": user_type, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- TOKEN VALIDATION (The fix for 401) ---
def get_current_user_cpf(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    load_persistence() # Essential to load David from JSON
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        cpf: str = payload.get("sub")
        if cpf is None:
            raise HTTPException(status_code=401, detail="Invalid token: sub missing")
        
        # Verify if user exists in the loaded memory
        if not any(str(p.get("cpf")) == str(cpf) for p in FAKE_PATIENTS_DB):
            raise HTTPException(status_code=401, detail="User not found in persistence")
            
        return cpf
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")