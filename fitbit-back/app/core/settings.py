import os
from dotenv import load_dotenv

load_dotenv()

SETTINGS = {
    "SECRET_KEY": os.getenv("JWT_SECRET", "your_super_secret_key_here"), 
    "ALGORITHM": os.getenv("JWT_ALGORITHM", "HS256"),
    "ACCESS_TOKEN_EXPIRE_MINUTES": int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
}