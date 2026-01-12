from fastapi import Depends, HTTPException, status, Request, Cookie, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.settings import SETTINGS 
from typing import Dict, Optional

# HTTPBearer creates a simple text box to paste the token in Swagger
security = HTTPBearer()

def get_cpf_from_header(authorization: Optional[str] = Header(None)) -> str:
    """
    Extracts CPF from Authorization header (alternative to HTTPBearer for CORS issues).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Remove 'Bearer ' prefix
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, SETTINGS["SECRET_KEY"], algorithms=[SETTINGS["ALGORITHM"]])
        cpf: str = payload.get("sub")
        
        if cpf is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
            
        return cpf
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )

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


def get_user_from_cookie(auth_token: Optional[str] = Cookie(None)) -> Dict[str, str]:
    """
    Decodes JWT from cookie (used for OAuth redirects where Authorization header is not available).
    Returns: {"sub": "cpf/crm", "type": "patient/doctor", "exp": timestamp}
    """
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please login first.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(auth_token, SETTINGS["SECRET_KEY"], algorithms=[SETTINGS["ALGORITHM"]])
        
        if payload.get("sub") is None or payload.get("type") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Please login again.",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
