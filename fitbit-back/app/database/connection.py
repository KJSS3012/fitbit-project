from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite database file (will be created in the root folder)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fitbit.db")
# For PostgreSQL later: "postgresql://user:password@localhost/dbname"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Needed only for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the DB session in requests
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
