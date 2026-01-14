-- Migration 002: Create patient_metrics table for Fitbit data
-- Purpose: Store synchronized Fitbit activity, heart rate, and sleep data

CREATE TABLE IF NOT EXISTS patient_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_cpf TEXT NOT NULL,
    date TEXT NOT NULL,
    steps INTEGER DEFAULT 0,
    hr_avg INTEGER DEFAULT 0,
    sleep_hours REAL DEFAULT 0.0,
    calories INTEGER DEFAULT 0,
    source TEXT DEFAULT 'fitbit',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (patient_cpf) REFERENCES patients(cpf) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_patient_metrics_cpf ON patient_metrics(patient_cpf);
CREATE INDEX IF NOT EXISTS idx_patient_metrics_date ON patient_metrics(date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_patient_metrics_cpf_date ON patient_metrics(patient_cpf, date);

-- Insert sample data for testing
INSERT OR IGNORE INTO patient_metrics (patient_cpf, date, steps, hr_avg, sleep_hours, calories, source)
VALUES 
    ('52998224725', '2026-01-09', 9500, 72, 7.4, 2300, 'fitbit'),
    ('52998224725', '2026-01-10', 10400, 77, 6.9, 2450, 'fitbit');
