from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="ITAM Backend")

app.include_router(auth.router)
