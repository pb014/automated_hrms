from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import true
from database import engine
import models

models.Base.metadata.create_all(bind = engine)

app = FastAPI(
    title="AI-Powered HRMS",
    description="Human Resource Management System with Gemini AI integration",
    version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers =["*"],
)

from routers.employees import router as employees_router

app.include_router(employees_router)

@app.get("/")
def root():
    return {
        "message": "HRMS API is running",
        "docs": "Visit /docs to explore all endpoints"
    }

@app.get("/health")
def health_check():
    return {"status" : "ok"}