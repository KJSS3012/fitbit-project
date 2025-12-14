from fastapi import FastAPI
from app.controllers import (auth_controller, fitbit_controller)

app = FastAPI()

app.include_router(auth_controller.router, prefix="/auth")
app.include_router(fitbit_controller.router, prefix="/fitbit")