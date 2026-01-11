-- Migration 003: Create data_authorization table for doctor-patient access control
-- Purpose: Manage which doctors can view which patients' health metrics

CREATE TABLE IF NOT EXISTS data_authorization (
    doctor_crm TEXT NOT NULL,
    patient_cpf TEXT NOT NULL,
    authorized INTEGER DEFAULT 1 NOT NULL,  -- SQLite uses INTEGER for BOOLEAN (0=false, 1=true)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (doctor_crm, patient_cpf),
    FOREIGN KEY (doctor_crm) REFERENCES doctors(crm) ON DELETE CASCADE,
    FOREIGN KEY (patient_cpf) REFERENCES patients(cpf) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_authorization_doctor ON data_authorization(doctor_crm);
CREATE INDEX IF NOT EXISTS idx_authorization_patient ON data_authorization(patient_cpf);

-- Insert sample authorization data for testing
-- Doctor CRM 12345SP authorized to view patient 52998224725 (from 002_fitbit_metrics.sql)
INSERT OR IGNORE INTO data_authorization (doctor_crm, patient_cpf, authorized)
VALUES 
    ('12345SP', '52998224725', 1),  -- Authorized
    ('12345SP', '12345678901', 0);  -- Not authorized (for 403 test)
