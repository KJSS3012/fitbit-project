from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import get_db

router = APIRouter()

@router.get("/health", tags=["System"], summary="Verifica saúde do sistema")
@router.head("/health", tags=["System"], summary="Verifica saúde do sistema")
def health_check(db: Session = Depends(get_db)):
    """
    Endpoint used by monitoring tools.
    Verify API status and database connectivity.
    """
    try:
        # Try execute a simple query to check database connectivity 
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "service": "Fitbit API"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )