import sys
import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# 1. Path setup (Same as your base)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.controllers.dashboard_controller import router
from app.api.dependencies import get_current_user_cpf

# 2. Setup the Test App
app = FastAPI()
app.include_router(router)

client = TestClient(app)

# 3. Security Mocking (The most important part)
def mock_get_current_user_cpf():
    return "12345678900"

# Apply the mock globally for this app instance
app.dependency_overrides[get_current_user_cpf] = mock_get_current_user_cpf


# --- TEST CASES ---

def test_read_dashboard_metrics_success():
    """
    Scenario: Authorized user requests metrics with valid period.
    Expected Result: Status 200 and correct JSON structure.
    """
    response = client.get("/metrics?period=daily")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "summary" in data
    assert "charts" in data
    assert data["period"] == "daily"

def test_read_dashboard_metrics_validation_error():
    """
    Scenario: User sends an invalid period parameter (e.g., 'yearly').
    Expected Result: Status 422 (Unprocessable Entity) due to regex validation.
    """
    response = client.get("/metrics?period=yearly")
    
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "String should match pattern '^(daily|weekly|monthly)$'"

def test_read_dashboard_metrics_unauthorized():
    """
    Scenario: Accessing the endpoint without a token (simulated).
    Expected Result: Status 401 Unauthorized.
    """
    
    # 1. Temporarily remove the mock to simulate "Not Logged In"
    app.dependency_overrides = {} 
    
    response = client.get("/metrics")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
    # 2. Restore the mock so other tests (if added later) don't break
    app.dependency_overrides[get_current_user_cpf] = mock_get_current_user_cpf