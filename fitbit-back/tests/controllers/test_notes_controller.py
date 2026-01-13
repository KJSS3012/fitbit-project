import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.controllers.notes_controller import router
from app.database.connection import Base, get_db

app = FastAPI()
app.include_router(router, prefix="/notes")

# Setup in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def db():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client with fresh database."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


import pytest
from sqlalchemy.orm import Session
from app.models.clinical_notes import ClinicalNote
from app.repositories.clinical_notes_repository import ClinicalNotesRepository
from app.controllers.notes_controller import CreateNoteRequest
from app.api.dependencies import get_current_user
import uuid
from datetime import datetime
import asyncio

def test_create_note_success(db: Session, client: TestClient):
    # Mock doctor user (JWT payload format)
    doctor_user = {"sub": "12345SP", "type": "doctor"}
    client.app.dependency_overrides[get_current_user] = lambda: doctor_user

    request_data = {
        "patient_cpf": "09876543210",
        "text": "Paciente apresentou melhora significativa",
        "metric_type": "hr",
        "start_date": "2024-01-01",
        "end_date": "2024-01-07"
    }

    response = client.post("/notes", json=request_data)
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "Anotação registrada com sucesso"}

def test_create_note_empty_text(db: Session, client: TestClient):
    doctor_user = {"sub": "12345SP", "type": "doctor"}
    client.app.dependency_overrides[get_current_user] = lambda: doctor_user

    request_data = {"patient_cpf": "09876543210", "text": ""}

    response = client.post("/notes", json=request_data)
    assert response.status_code == 400
    assert "Texto da anotação não pode ser vazio" in response.json()["detail"]

def test_create_note_unauthorized(db: Session, client: TestClient):
    patient_user = {"cpf": "09876543210", "type": "paciente"}
    client.app.dependency_overrides[get_current_user] = lambda: patient_user

    request_data = {"patient_cpf": "09876543210", "text": "Nota"}

    response = client.post("/notes", json=request_data)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_notes_patient(db: Session, client: TestClient):
    # Create a note
    repo = ClinicalNotesRepository(db)
    note = ClinicalNote(
        id=str(uuid.uuid4()),
        patient_cpf="09876543210",
        doctor_crm="12345SP",
        text="Nota de teste",
        created_at=datetime.now()
    )
    await repo.create_note(note)

    # Mock patient user (JWT payload format)
    patient_user = {"sub": "09876543210", "type": "patient"}
    client.app.dependency_overrides[get_current_user] = lambda: patient_user

    response = client.get("/notes/09876543210")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["text"] == "Nota de teste"

@pytest.mark.asyncio
async def test_delete_note_success(db: Session, client: TestClient):
    # Create a note
    repo = ClinicalNotesRepository(db)
    note = ClinicalNote(
        id=str(uuid.uuid4()),
        patient_cpf="09876543210",
        doctor_crm="12345SP",
        text="Nota para deletar",
        created_at=datetime.now()
    )
    await repo.create_note(note)

    # Mock doctor user (JWT payload format)
    doctor_user = {"sub": "12345SP", "type": "doctor"}
    client.app.dependency_overrides[get_current_user] = lambda: doctor_user

    response = client.delete(f"/notes/{note.id}")
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "Anotação excluída com sucesso"}

    # Verify note is deleted
    deleted_note = db.query(ClinicalNote).filter(ClinicalNote.id == note.id).first()
    assert deleted_note is None

def test_delete_note_not_found(db: Session, client: TestClient):
    doctor_user = {"sub": "12345SP", "type": "doctor"}
    client.app.dependency_overrides[get_current_user] = lambda: doctor_user

    response = client.delete("/notes/nonexistent-id")
    assert response.status_code == 404
    assert "Anotação não encontrada" in response.json()["detail"]

def test_delete_note_unauthorized(db: Session, client: TestClient):
    patient_user = {"sub": "09876543210", "type": "patient"}
    client.app.dependency_overrides[get_current_user] = lambda: patient_user

    response = client.delete("/notes/some-id")
    assert response.status_code == 403
    assert "Apenas médicos podem excluir anotações" in response.json()["detail"]