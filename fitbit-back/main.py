from fastapi import FastAPI
from app.controllers.auth_controller import router as auth_router
from app.controllers.fitbit_controller import router as fitbit_router

app = FastAPI()

# Rotas
app.include_router(auth_router, prefix="/auth")
app.include_router(fitbit_router, prefix="/fitbit")

@app.get("/")
def read_root():
    return {"message": "API is running!"}
