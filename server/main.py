from models import (
    Employee, Document,
    JobPosting, Candidate,
    LeaveRequest, LeaveBalance, Attendance,
    ReviewCycle, EmployeeReview,
    OnboardingChecklist, ChecklistProgress, PolicyDocument, ChatLog
)
from routers import employees, leave, recruitment, performance, onboarding, analytics
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import true
from database import engine
import models
import os

models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI-Powered HRMS",
    description="Human Resource Management System with Gemini AI integration",
    version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/resumes", exist_ok=True)
os.makedirs("uploads/documents", exist_ok=True)
os.makedirs("uploads/policies", exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(
    employees.router, prefix="/api/employees", tags=["Employees"]
)

app.include_router(
    recruitment.router, prefix="/api/recruitment", tags=["Recruitment"]
)

app.include_router(
    leave.router, prefix="/api/leave", tags=["Leave & Attendance"]
)

app.include_router(
    performance.router, prefix="/api/performance", tags=["Performance"]
)

app.include_router(
    onboarding.router, prefix="/api/onboarding", tags=["Onboarding"]
)

app.include_router(
    analytics.router, prefix="/api/analytics", tags=["Analytics"]
)


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
    return {"status": "ok"}
