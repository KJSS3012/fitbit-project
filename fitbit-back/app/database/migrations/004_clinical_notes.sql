-- Migration: 004_clinical_notes.sql
CREATE TABLE clinical_notes (
    id VARCHAR PRIMARY KEY,
    patient_cpf VARCHAR NOT NULL,
    doctor_crm VARCHAR NOT NULL,
    text TEXT NOT NULL,
    metric_type VARCHAR,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_clinical_notes_patient_cpf ON clinical_notes (patient_cpf);
CREATE INDEX idx_clinical_notes_doctor_crm ON clinical_notes (doctor_crm);