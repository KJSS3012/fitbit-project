from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.auth_controller import router as auth_router
from app.controllers.fitbit_controller import router as fitbit_router
from app.controllers.dashboard_controller import router as dashboard_router
from app.controllers.user_controller import router as user_router
from app.controllers.authorization_controller import router as authorization_router
from app.controllers.export_controller import router as export_router

from app.database.connection import Base, engine

app = FastAPI()


# =========================
# Startup
# =========================
@app.on_event("startup")
def startup_event():
    # Cria as tabelas no banco de dados
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


# =========================
# CORS
# =========================
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Routers
# =========================
app.include_router(auth_router, prefix="/auth")
app.include_router(authorization_router, prefix="/auth")
app.include_router(fitbit_router, prefix="/fitbit")
app.include_router(dashboard_router, prefix="/dashboard")
app.include_router(user_router, prefix="/user")
app.include_router(export_router)


# =========================
# Root
# =========================
@app.get("/")
def read_root():
    return {"message": "API is running!"}
