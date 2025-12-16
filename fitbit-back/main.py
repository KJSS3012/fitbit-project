from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.auth_controller import router as auth_router
from app.controllers.fitbit_controller import router as fitbit_router

app = FastAPI()

# Configuração de CORS para permitir requisições do Nuxt
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, OPTIONS etc.
    allow_headers=["*"],
)

# Rotas
app.include_router(auth_router, prefix="/auth")
app.include_router(fitbit_router, prefix="/fitbit")

# Rota raiz para teste
@app.get("/")
def read_root():
    return {"message": "API is running!"}
