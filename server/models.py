from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Boolean, Float,
    ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime, date

from database import Base


# Module-1:

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    designation = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    joining_date = Column(Date, nullable=False)
    contact = Column(String(20))

    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    bio = Column(Text, nullable=True)   # AI writes this from profile data

    is_active = Column(Boolean, default=True)
    termination_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    manager = relationship("Employee", remote_side=[
                           id], backref="subordinates")

    documents = relationship("Document", back_populates="employee")

    leave_requests = relationship("LeaveRequest", back_populates="employee")

    leave_balances = relationship("LeaveBalance", back_populates="employee")

    attendance_records = relationship("Attendance", back_populates="employee")

    reviews = relationship("EmployeeReview", back_populates="employee")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    doc_type = Column(String(50))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="documents")


# MODULE-2


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(Text, nullable=False)
    experience_level = Column(String(50))
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)

    candidates = relationship("Candidate", back_populates="job")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    resume_path = Column(String(500))

    stage = Column(String(20), default="applied")

    match_score = Column(Float, nullable=True)
    strengths = Column(Text, nullable=True)
    gaps = Column(Text, nullable=True)
    interview_questions = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("JobPosting", back_populates="candidates")


# MODULE-3

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(String(20), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text)
    status = Column(String(20), default="pending")
    manager_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="leave_requests")


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    leave_type = Column(String(20), nullable=False)
    total = Column(Integer, default=12)
    used = Column(Integer, default=0)

    employee = relationship("Employee", back_populates="leave_balances")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)

    employee = relationship("Employee", back_populates="attendance_records")


# MODULE-4

class ReviewCycle(Base):
    __tablename__ = "review_cycles"

    id = Column(Integer, primary_key=True, index=True)
    period_name = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship("EmployeeReview", back_populates="cycle")


class EmployeeReview(Base):
    __tablename__ = "employee_reviews"

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("review_cycles.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    self_assessment = Column(Text, nullable=True)
    self_rating = Column(Float, nullable=True)

    manager_ratings = Column(JSON, nullable=True)
    manager_comment = Column(Text, nullable=True)

    ai_summary = Column(Text, nullable=True)
    ai_flags = Column(Text, nullable=True)
    ai_development_actions = Column(
        Text, nullable=True)

    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    cycle = relationship("ReviewCycle", back_populates="reviews")
    employee = relationship("Employee", back_populates="reviews")


# MODULE-5

class OnboardingChecklist(Base):
    __tablename__ = "onboarding_checklists"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(100), nullable=False)
    items = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    progress_records = relationship(
        "ChecklistProgress", back_populates="checklist")


class ChecklistProgress(Base):
    __tablename__ = "checklist_progress"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    checklist_id = Column(Integer, ForeignKey(
        "onboarding_checklists.id"), nullable=False)
    completed_items = Column(JSON, default=[])
    started_at = Column(DateTime, default=datetime.utcnow)

    checklist = relationship("OnboardingChecklist",
                             back_populates="progress_records")
    employee = relationship("Employee")


class PolicyDocument(Base):
    __tablename__ = "policy_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    raw_text = Column(Text, nullable=True)
    embedding_stored = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    could_answer = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee")
