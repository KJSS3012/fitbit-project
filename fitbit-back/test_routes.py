from fastapi.testclient import TestClient
from main import app
from app.core.security import get_current_user_cpf

def override_get_current_user_cpf():
    return "12345678901"

app.dependency_overrides[get_current_user_cpf] = override_get_current_user_cpf
client = TestClient(app)

# Test /fitbit/auth
r1 = client.get('/fitbit/auth?cpf=123')
print(f'/fitbit/auth - Status: {r1.status_code}, Location: {r1.headers.get("location")}')

# Test /fitbit/callback
r2 = client.get('/fitbit/callback?error=access_denied&state=123')
print(f'/fitbit/callback denied - Status: {r2.status_code}, Location: {r2.headers.get("location")}')

# Test /fitbit/status
r3 = client.get('/fitbit/status')
print(f'/fitbit/status - Status: {r3.status_code}')
