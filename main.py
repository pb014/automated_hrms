from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import true
from database import engine
import models
import os

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

os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/resumes", exist_ok=True)
os.makedirs("uploads/documents", exist_ok=True)
os.makedirs("uploads/policies", exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

from routers import employees
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])

@app.get("/")
def root():
    return {
        "message": "AI-Powered HRMS API is running!",
        "docs": "Visit /docs for interactive API documentation",
        "modules": [
            "Employee Records",
            "Recruitment & ATS",
            "Leave & Attendance",
            "Performance Reviews",
            "Onboarding Assistant",
            "HR Analytics"
        ]
    }

@app.get("/health")
def health_check():
    return {"status" : "ok"}