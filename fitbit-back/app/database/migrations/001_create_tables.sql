-- Inicialização das tabelas
-- Tabela de Pacientes
CREATE TABLE IF NOT EXISTS patients (
    cpf VARCHAR(11) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    password VARCHAR(255) NOT NULL,
    fitbit_access_token VARCHAR(512),
    fitbit_refresh_token VARCHAR(512),
    fitbit_expires_at REAL
);

-- Tabela de Médicos
CREATE TABLE IF NOT EXISTS doctors (
    cpf VARCHAR(11) PRIMARY KEY,
    crm VARCHAR(8) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_doctors_crm ON doctors(crm);