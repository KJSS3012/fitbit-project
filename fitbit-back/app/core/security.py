import os
from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.mock import FAKE_PATIENTS_DB
from app.core.fitbit_client import load_persistence

# =========================
# JWT Settings (from .env)
# =========================
JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))

security_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =========================
# PASSWORD LOGIC
# =========================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# =========================
# TOKEN GENERATION
# =========================
def create_access_token(subject: Union[str, Any], user_type: str) -> str:
    """
    Create a JWT access token.
    user_type: "patient" or "doctor"
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "type": user_type,
        "exp": expire,
    }

    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


# =========================
# TOKEN VALIDATION
# =========================
def get_current_user_cpf(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
):
    """
    Validates JWT and returns CPF stored in `sub`
    """
    load_persistence()  # Load persisted Fitbit + users

    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        cpf: str = payload.get("sub")
        if not cpf:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: subject missing",
            )

        # Ensure user exists
        if not any(str(p.get("cpf")) == str(cpf) for p in FAKE_PATIENTS_DB):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return cpf

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
        )
