from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.settings import SETTINGS 

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