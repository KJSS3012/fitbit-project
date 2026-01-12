"""Execute migration 003 - data_authorization table"""
from app.database.connection import engine
from pathlib import Path
from sqlalchemy import text
import re

migration_file = Path('app/database/migrations/003_authorization.sql')
migration_sql = migration_file.read_text()

# Remove comments and split into statements
lines = [line for line in migration_sql.split('\n') if not line.strip().startswith('--')]
clean_sql = '\n'.join(lines)

# Split by semicolon but keep complete statements
statements = []
current_statement = []
for line in clean_sql.split('\n'):
    if line.strip():
        current_statement.append(line)
        if ';' in line:
            stmt = '\n'.join(current_statement)
            if stmt.strip():
                statements.append(stmt)
            current_statement = []

with engine.connect() as conn:
    for statement in statements:
        statement = statement.strip()
        if statement:
            print(f"Executing: {statement[:50]}...")
            conn.execute(text(statement))
    conn.commit()
    
print('✅ Migration 003 executed successfully')
print('   - Created table: data_authorization')
print('   - Created indexes: idx_authorization_doctor, idx_authorization_patient')
print('   - Sample data: doctor_crm=12345SP authorized for patient_cpf=52998224725')
