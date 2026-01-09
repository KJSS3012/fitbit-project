from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.settings import SETTINGS 

# Defines that the token comes from the patient login route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/patient")

def get_current_user_cpf(token: str = Depends(oauth2_scheme)) -> str:
    """
    Decodifica o Token JWT para descobrir quem está logado.
    Usado pelo Dashboard para saber de qual CPF buscar os dados.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodifies the token
        payload = jwt.decode(token, SETTINGS["SECRET_KEY"], algorithms=[SETTINGS["ALGORITHM"]])
        
        cpf: str = payload.get("sub")
        
        if cpf is None:
            raise credentials_exception
            
        return cpf
        
    except JWTError:
        raise credentials_exception