import os
import json
from unittest.mock import patch
from app.core.fitbit_client import save_persistence, load_persistence
from app.models.mock import FAKE_PATIENTS_DB

TEST_DATA_FILE = "test_patients_data.json"

def test_save_and_load_persistence():
    """Verify cycle of saving to and loading from the persistence file."""
    
    with patch("app.core.fitbit_client.DATA_FILE", TEST_DATA_FILE):
        
        FAKE_PATIENTS_DB.clear()
        test_user = {"cpf": "999", "name": "TEST_USER", "fitbit_access_token": "abc"}
        FAKE_PATIENTS_DB.append(test_user)
        
        save_persistence()
        assert os.path.exists(TEST_DATA_FILE)
        
        FAKE_PATIENTS_DB.clear()
        load_persistence()
        
        assert len(FAKE_PATIENTS_DB) == 1
        assert FAKE_PATIENTS_DB[0]["cpf"] == "999"
        assert FAKE_PATIENTS_DB[0]["name"] == "TEST_USER"
        
        if os.path.exists(TEST_DATA_FILE):
            os.remove(TEST_DATA_FILE)

def test_load_persistence_file_not_found():
    """Verify if the persistence file is missing, it gets created."""
    with patch("app.core.fitbit_client.DATA_FILE", "non_existent.json"):
        if os.path.exists("non_existent.json"):
            os.remove("non_existent.json")
            
        load_persistence()
        assert os.path.exists("non_existent.json")
        os.remove("non_existent.json")