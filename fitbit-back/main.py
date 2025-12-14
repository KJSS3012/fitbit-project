from fastapi import FastAPI
from app.controllers.auth_controller import router as auth_router

app = FastAPI()

# Include the authentication routes in the main application
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "API is running!"}