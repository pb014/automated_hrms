from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime


# Employee Schemas

class EmployeeCreate(BaseModel):
    name: str
    email: str
    designation: str
    department: str
    joining_date: date
    contact: Optional[str] = None
    manager_id: Optional[int] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    contact: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None
    termination_date: Optional[date] = None


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    designation: str
    department: str
    joining_date: date
    contact: Optional[str]
    manager_id: Optional[int]
    bio: Optional[str]
    is_active: bool
    termination_date: Optional[date]
    created_at: datetime

    model_config = {"from_attributes": True}


class EmployeeListResponse(BaseModel):
    id: int
    name: str
    email: str
    designation: str
    department: str
    is_active: bool
    joining_date: date
    manager_id: Optional[int]

    model_config = {"from_attributes": True}


# Document Schemas

class DocumentResponse(BaseModel):
    id: int
    employee_id: int
    filename: str
    file_path: str
    doc_type: Optional[str]
    uploaded_at: datetime

    model_config = {"from_attributes": True}


# Recruitment Schemas

class JobPostingCreate(BaseModel):
    role: str
    description: str
    required_skills: str
    experience_level: Optional[str] = None


class JobPostingResponse(BaseModel):
    id: int
    role: str
    description: str
    required_skills: str
    experience_level: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateCreate(BaseModel):
    job_id: int
    name: str
    email: Optional[str] = None


class CandidateResponse(BaseModel):
    id: int
    job_id: int
    name: str
    email: Optional[str]
    resume_path: Optional[str]
    stage: str
    match_score: Optional[float]
    strengths: Optional[str]
    gaps: Optional[str]
    interview_questions: Optional[str]
    ai_summary: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateStageUpdate(BaseModel):
    stage: str    # applied/screening/interview/offer/hired/rejected


# Leave & Attendance Schemas

class LeaveRequestCreate(BaseModel):
    employee_id: int
    leave_type: str          # sick/casual/earned/wfh
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveRequestResponse(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str]
    status: str
    manager_comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class LeaveApproval(BaseModel):
    status: str
    manager_comment: Optional[str] = None


class LeaveBalanceResponse(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    total: int
    used: int

    model_config = {"from_attributes": True}


class AttendanceCreate(BaseModel):
    employee_id: int
    date: date
    status: str


class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    date: date
    status: str

    model_config = {"from_attributes": True}


# Performance Review Schemas

class ReviewCycleCreate(BaseModel):
    period_name: str
    start_date: date
    end_date: date


class ReviewCycleResponse(BaseModel):
    id: int
    period_name: str
    start_date: date
    end_date: date
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SelfAssessmentSubmit(BaseModel):
    self_assessment: str
    self_rating: float        # 1-5


class ManagerReviewSubmit(BaseModel):
    manager_ratings: dict     # {"quality": 4, "delivery": 3, ...}
    manager_comment: Optional[str] = None


class EmployeeReviewResponse(BaseModel):
    id: int
    cycle_id: int
    employee_id: int
    self_assessment: Optional[str]
    self_rating: Optional[float]
    manager_ratings: Optional[dict]
    manager_comment: Optional[str]
    ai_summary: Optional[str]
    ai_flags: Optional[str]
    ai_development_actions: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Onboarding Schemas
class ChecklistCreate(BaseModel):
    role: str
    # [{"task": "...", "due_days": 3, "assignee": "HR"}, ...]
    items: list


class ChecklistResponse(BaseModel):
    id: int
    role: str
    items: list
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    employee_id: Optional[int] = None
    question: str


class ChatResponse(BaseModel):
    answer: str
    could_answer: bool


class ChatLogResponse(BaseModel):
    id: int
    employee_id: Optional[int]
    question: str
    answer: str
    could_answer: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PolicyDocumentResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    embedding_stored: bool
    uploaded_at: datetime

    model_config = {"from_attributes": True}
