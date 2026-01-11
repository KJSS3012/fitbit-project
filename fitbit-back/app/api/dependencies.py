from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.settings import SETTINGS 
from typing import Dict

# HTTPBearer creates a simple text box to paste the token in Swagger
security = HTTPBearer()

def get_current_user_cpf(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Decodes the JWT Token to identify who is logged in.
    """
    token = credentials.credentials  # Extracts the token string
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodes the token
        payload = jwt.decode(token, SETTINGS["SECRET_KEY"], algorithms=[SETTINGS["ALGORITHM"]])
        
        cpf: str = payload.get("sub")
        
        if cpf is None:
            raise credentials_exception
            
        return cpf
        
    except JWTError:
        raise credentials_exception


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, str]:
    """
    Decodes the JWT Token and returns full user info.
    Returns: {"sub": "cpf/crm", "type": "patient/doctor", "exp": timestamp}
    """
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SETTINGS["SECRET_KEY"], algorithms=[SETTINGS["ALGORITHM"]])
        
        if payload.get("sub") is None or payload.get("type") is None:
            raise credentials_exception
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception
