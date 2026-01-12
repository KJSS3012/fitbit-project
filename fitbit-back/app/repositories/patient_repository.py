from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.models.patient_metrics import PatientMetrics
from app.schemas.auth_schema import PatientCreate
from datetime import datetime
from typing import List, Dict, Any

class PatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, patient_data: PatientCreate, password_hash: str) -> Patient:
        db_patient = Patient(
            cpf=patient_data.cpf,
            name=patient_data.name,
            password=password_hash
        )
        self.db.add(db_patient)
        self.db.commit()
        self.db.refresh(db_patient)
        return db_patient

    def find_by_cpf(self, cpf: str) -> Patient | None:
        return self.db.query(Patient).filter(Patient.cpf == cpf).first()
    
    def update_fitbit_tokens(
        self, 
        cpf: str, 
        access_token: str, 
        refresh_token: str, 
        expires_at: float
    ) -> Patient | None:
        """Update Fitbit OAuth tokens for a patient."""
        patient = self.find_by_cpf(cpf)
        if not patient:
            return None
        
        patient.fitbit_access_token = access_token
        patient.fitbit_refresh_token = refresh_token
        patient.fitbit_expires_at = expires_at
        
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    def remove_fitbit_tokens(self, cpf: str) -> Patient | None:
        """Remove Fitbit tokens (disconnect)."""
        patient = self.find_by_cpf(cpf)
        if not patient:
            return None
        
        patient.fitbit_access_token = None
        patient.fitbit_refresh_token = None
        patient.fitbit_expires_at = None
        

    def save_metrics(self, cpf: str, metrics_list: List[Dict[str, Any]]) -> List[PatientMetrics]:
        """Save or update Fitbit metrics data for a patient.
        
        Args:
            cpf: Patient CPF
            metrics_list: List of dictionaries with keys: date, steps, hr_avg, sleep_hours, calories
        
        Returns:
            List of saved PatientMetrics objects
        """
        saved_metrics = []
        
        for metric_data in metrics_list:
            # Check if metric already exists for this date
            existing_metric = self.db.query(PatientMetrics).filter(
                PatientMetrics.patient_cpf == cpf,
                PatientMetrics.date == metric_data.get("date")
            ).first()
            
            if existing_metric:
                # Update existing
                existing_metric.steps = metric_data.get("steps", 0)
                existing_metric.hr_avg = metric_data.get("hr_avg", 0)
                existing_metric.sleep_hours = metric_data.get("sleep_hours", 0.0)
                existing_metric.calories = metric_data.get("calories", 0)
                existing_metric.source = metric_data.get("source", "fitbit")
                existing_metric.updated_at = datetime.utcnow()
                saved_metrics.append(existing_metric)
            else:
                # Create new
                new_metric = PatientMetrics(
                    patient_cpf=cpf,
                    date=metric_data.get("date"),
                    steps=metric_data.get("steps", 0),
                    hr_avg=metric_data.get("hr_avg", 0),
                    sleep_hours=metric_data.get("sleep_hours", 0.0),
                    calories=metric_data.get("calories", 0),
                    source=metric_data.get("source", "fitbit")
                )
                self.db.add(new_metric)
                saved_metrics.append(new_metric)
        
        self.db.commit()
        
        # Refresh all objects
        for metric in saved_metrics:
            self.db.refresh(metric)
        
        return saved_metrics

    def get_metrics(self, cpf: str, start_date: str = None, end_date: str = None) -> List[PatientMetrics]:
        """Retrieve metrics for a patient within a date range.
        
        Args:
            cpf: Patient CPF
            start_date: Start date (YYYY-MM-DD) - optional
            end_date: End date (YYYY-MM-DD) - optional
        
        Returns:
            List of PatientMetrics ordered by date
        """
        query = self.db.query(PatientMetrics).filter(PatientMetrics.patient_cpf == cpf)
        
        if start_date:
            query = query.filter(PatientMetrics.date >= start_date)
        if end_date:
            query = query.filter(PatientMetrics.date <= end_date)
        
        return query.order_by(PatientMetrics.date.desc()).all()

        self.db.commit()
        self.db.refresh(patient)
        return patient
