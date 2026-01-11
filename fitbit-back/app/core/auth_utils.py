import os
from jose import jwt, JWTError
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.mock import FAKE_PATIENTS_DB
from app.core.fitbit_client import load_persistence

SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

security_scheme = HTTPBearer()

def get_current_user_cpf(res: HTTPAuthorizationCredentials = Depends(security_scheme)):
    load_persistence()
    token = res.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        cpf = str(payload.get("sub"))
        
        user_exists = any(str(p.get("cpf")) == cpf for p in FAKE_PATIENTS_DB)
        
        if not user_exists:
            raise HTTPException(status_code=401, detail="User not found")
            
        return cpf
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")