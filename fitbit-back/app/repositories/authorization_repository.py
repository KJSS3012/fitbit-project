from sqlalchemy.orm import Session
from app.models.data_authorization import DataAuthorization
from app.models.doctor import Doctor
from app.models.patient import Patient
from typing import List, Dict
import json
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import logging


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

    def get_patients_by_doctor(self, doctor_crm: str) -> List[Dict]:
        """Get list of patients authorized for doctor with their details.
        
        Args:
            doctor_crm: Doctor's CRM number
            
        Returns:
            List of dicts: [{"cpf": str, "name": str}]
        """
        authorizations = (
            self.db.query(DataAuthorization, Patient.cpf, Patient.name)
            .join(Patient, DataAuthorization.patient_cpf == Patient.cpf)
            .filter(DataAuthorization.doctor_crm == doctor_crm, DataAuthorization.authorized == True)
            .all()
        )
        
        return [
            {
                "cpf": patient_cpf,
                "name": patient_name
            }
            for auth, patient_cpf, patient_name in authorizations
        ]

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

    def get_patient_authorized_doctors(self, patient_cpf: str) -> List[Dict]:
        """Get list of doctors with authorization status for patient.
        
        Args:
            patient_cpf: Patient's CPF
            
        Returns:
            List of dicts: [{"crm": str, "doctor_name": str, "authorized": bool}]
        """
        authorizations = (
            self.db.query(DataAuthorization, Doctor.name)
            .join(Doctor, DataAuthorization.doctor_crm == Doctor.crm)
            .filter(DataAuthorization.patient_cpf == patient_cpf)
            .all()
        )
        
        return [
            {
                "crm": auth.doctor_crm,
                "doctor_name": doctor_name,
                "authorized": auth.authorized
            }
            for auth, doctor_name in authorizations
        ]

    def toggle_authorization_with_audit(self, doctor_crm: str, patient_cpf: str) -> Dict:
        """Toggle doctor authorization and log audit trail.
        
        Args:
            doctor_crm: Doctor's CRM number
            patient_cpf: Patient's CPF
            
        Returns:
            Dict with new status: {"authorized": bool, "action": str}
        """
        auth = self.db.query(DataAuthorization).filter(
            DataAuthorization.doctor_crm == doctor_crm,
            DataAuthorization.patient_cpf == patient_cpf
        ).first()
        
        if not auth:
            raise ValueError(f"Autorização não encontrada para CRM {doctor_crm}")
        
        # Toggle authorization
        new_status = not auth.authorized
        auth.authorized = new_status
        
        # Append audit log
        action = "grant" if new_status else "revoke"
        audit_entry = {
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "by": "patient"
        }
        
        if auth.audit_log:
            try:
                audit_list = json.loads(auth.audit_log)
            except json.JSONDecodeError:
                audit_list = []
        else:
            audit_list = []
        
        audit_list.append(audit_entry)
        auth.audit_log = json.dumps(audit_list)
        
        # Transactional commit
        try:
            self.db.commit()
            self.db.refresh(auth)
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Erro ao registrar auditoria: {str(e)}")
        
        return {"authorized": new_status, "action": action}

    def grant_new_authorization(self, doctor_crm: str, patient_cpf: str) -> DataAuthorization:
        """Create new authorization for doctor-patient pair.
        
        Args:
            doctor_crm: Doctor's CRM number
            patient_cpf: Patient's CPF
            
        Returns:
            Created DataAuthorization object
        """
        # Check if already exists
        existing = self.db.query(DataAuthorization).filter(
            DataAuthorization.doctor_crm == doctor_crm,
            DataAuthorization.patient_cpf == patient_cpf
        ).first()
        
        if existing:
            raise ValueError(f"Médico {doctor_crm} já está vinculado")
        
        # Create with audit
        audit_entry = {
            "action": "grant",
            "timestamp": datetime.utcnow().isoformat(),
            "by": "patient"
        }
        
        db_auth = DataAuthorization(
            doctor_crm=doctor_crm,
            patient_cpf=patient_cpf,
            authorized=True,
            audit_log=json.dumps([audit_entry])
        )
        
        self.db.add(db_auth)
        try:
            self.db.commit()
            self.db.refresh(db_auth)
            return db_auth
        except IntegrityError as e:
            # Likely a foreign key or constraint violation (doctor/patient missing)
            self.db.rollback()
            logging.exception("IntegrityError while granting authorization")
            raise ValueError(f"Falha ao criar autorização: {str(e.orig)}")
        except Exception as e:
            self.db.rollback()
            logging.exception("Unexpected error while granting authorization")
            raise RuntimeError(f"Erro interno ao criar autorização: {str(e)}")

    def revoke_all_authorizations(self, patient_cpf: str) -> int:
        """Revoke all doctor authorizations for a patient.
        
        Args:
            patient_cpf: Patient's CPF
            
        Returns:
            Number of authorizations revoked
        """
        # Get all authorized doctors for this patient
        authorizations = self.db.query(DataAuthorization).filter(
            DataAuthorization.patient_cpf == patient_cpf,
            DataAuthorization.authorized == True
        ).all()
        
        revoked_count = 0
        
        for auth in authorizations:
            # Revoke authorization
            auth.authorized = False
            
            # Append audit log
            audit_entry = {
                "action": "revoke_all",
                "timestamp": datetime.utcnow().isoformat(),
                "by": "patient"
            }
            
            if auth.audit_log:
                try:
                    audit_list = json.loads(auth.audit_log)
                except json.JSONDecodeError:
                    audit_list = []
            else:
                audit_list = []
            
            audit_list.append(audit_entry)
            auth.audit_log = json.dumps(audit_list)
            
            revoked_count += 1
        
        # Commit all changes
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Erro ao revogar autorizações: {str(e)}")
        
        return revoked_count
