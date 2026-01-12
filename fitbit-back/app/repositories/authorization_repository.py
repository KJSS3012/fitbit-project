from sqlalchemy.orm import Session
from app.models.data_authorization import DataAuthorization
from typing import List


class AuthorizationRepository:
    """Repository for managing doctor-patient data authorization."""
    
    def __init__(self, db: Session):
        self.db = db

    def check_authorization(self, doctor_crm: str, patient_cpf: str) -> bool:
        """Check if doctor is authorized to view patient's data.
        
        Args:
            doctor_crm: Doctor's CRM number
            patient_cpf: Patient's CPF
            
        Returns:
            True if authorized, False otherwise
        """
        authorization = self.db.query(DataAuthorization).filter(
            DataAuthorization.doctor_crm == doctor_crm,
            DataAuthorization.patient_cpf == patient_cpf
        ).first()
        
        if not authorization:
            return False
            
        return authorization.authorized

    def get_authorized_patients(self, doctor_crm: str) -> List[str]:
        """Get list of patient CPFs that doctor is authorized to view.
        
        Args:
            doctor_crm: Doctor's CRM number
            
        Returns:
            List of patient CPF strings
        """
        authorizations = self.db.query(DataAuthorization).filter(
            DataAuthorization.doctor_crm == doctor_crm,
            DataAuthorization.authorized == True
        ).all()
        
        return [auth.patient_cpf for auth in authorizations]

    def create_authorization(self, doctor_crm: str, patient_cpf: str, authorized: bool = True) -> DataAuthorization:
        """Create new authorization record.
        
        Args:
            doctor_crm: Doctor's CRM number
            patient_cpf: Patient's CPF
            authorized: Whether access is authorized (default True)
            
        Returns:
            Created DataAuthorization object
        """
        db_auth = DataAuthorization(
            doctor_crm=doctor_crm,
            patient_cpf=patient_cpf,
            authorized=authorized
        )
        self.db.add(db_auth)
        self.db.commit()
        self.db.refresh(db_auth)
        return db_auth

    def update_authorization(self, doctor_crm: str, patient_cpf: str, authorized: bool) -> DataAuthorization | None:
        """Update existing authorization status.
        
        Args:
            doctor_crm: Doctor's CRM number
            patient_cpf: Patient's CPF
            authorized: New authorization status
            
        Returns:
            Updated DataAuthorization or None if not found
        """
        auth = self.db.query(DataAuthorization).filter(
            DataAuthorization.doctor_crm == doctor_crm,
            DataAuthorization.patient_cpf == patient_cpf
        ).first()
        
        if not auth:
            return None
            
        auth.authorized = authorized
        self.db.commit()
        self.db.refresh(auth)
        return auth

    def revoke_authorization(self, doctor_crm: str, patient_cpf: str) -> bool:
        """Revoke doctor's access to patient data.
        
        Args:
            doctor_crm: Doctor's CRM number
            patient_cpf: Patient's CPF
            
        Returns:
            True if revoked successfully, False if not found
        """
        result = self.update_authorization(doctor_crm, patient_cpf, False)
        return result is not None
