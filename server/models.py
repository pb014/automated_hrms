from annotated_types import T
from sqlalchemy import(
    Column, Integer, String,Text, Float, Boolean, Date, DateTime, ForeignKey, JSON, column, null, true
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

#Module - 1
class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    designation = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    joining_date = Column(Date, nullable=False)
    manager_id    = Column(Integer, ForeignKey("employees.id"), nullable=True)  
    
    contact = Column(String(20))                     
    bio           = Column(Text, nullable=True)                         
    is_active     = Column(Boolean, default=True)
    termination_date = Column(Date, nullable=True)
    created_at    = Column(DateTime, default=func.now())

    documents = relationship("Document", back_populates="employee")
    
    manager = relationship("Employee", remote_side=[id], backref="reports")
    
    leave_requests = relationship("LeaveRequest", back_populates="employee")
    
    leave_balances = relationship("LeaveBalance", back_populates="employee")
    
    attendance_records = relationship("Attendance", back_populates="employee")
    
    reviews = relationship("EmployeeReview", back_populates="employee")

class Document(Base):
    __tablename__ = "documents"
 
    id            = Column(Integer, primary_key=True, index=True)
    employee_id   = Column(Integer, ForeignKey("employees.id"), nullable=False)
    filename      = Column(String(255), nullable=False)                        
    file_path     = Column(String(500), nullable=False)                        
    doc_type      = Column(String(50))                        
    uploaded_at   = Column(DateTime, default=func.now())
 
    employee      = relationship("Employee", back_populates="documents")


#Module-2
class JobPosting(Base):
    __tablename__ = "job_postings"
 
    id              = Column(Integer, primary_key=True, index=True)
    role            = Column(String(100), nullable=False)      
    description     = Column(Text, nullable=False)                        
    required_skills = Column(Text, nullable=False)                      
    experience_level= Column(String(50))                      
    status          = Column(String(20), default="open")      
    created_at      = Column(DateTime, default=func.now())
 
    candidates      = relationship("Candidate", back_populates="job")

class Candidate(Base):
    __tablename__ = "candidates"
 
    id                   = Column(Integer, primary_key=True, index=True)
    job_id               = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    name                 = Column(String(100), nullable=False)
    email                = Column(String(100))
    resume_path          = Column(String(500))                 
    stage                = Column(String(20), default="Applied")     # Applied → Screening → Interview → Offer → HiredRejected
    match_score          = Column(Float, nullable=True)   
    match_reasoning      = Column(Text, nullable=True)    
    strengths            = Column(JSON, nullable=True)    
    gaps                 = Column(JSON, nullable=True)    
    interview_questions  = Column(JSON, nullable=True)    
    applied_at           = Column(DateTime, default=func.now())
 
    job                  = relationship("JobPosting", back_populates="candidates")


#Module-3
class LeaveRequest(Base):
    __tablename__ = "leave_requests"
 
    id              = Column(Integer, primary_key=True, index=True)
    employee_id     = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type      = Column(String)                      
    start_date      = Column(Date, nullable=False)
    end_date        = Column(Date, nullable=False)
    reason          = Column(Text)
    status          = Column(String, default="pending")   
    manager_comment = Column(Text, nullable=True)
    ai_flag         = Column(Text, nullable=True)         
    created_at      = Column(DateTime, default=func.now())
 
    employee        = relationship("Employee")
 
 
class LeaveBalance(Base):
    __tablename__ = "leave_balances"
 
    id          = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type  = Column(String)                          
    total       = Column(Integer, default=0)              
    used        = Column(Integer, default=0)              
 
    employee    = relationship("Employee")
 
 
class Attendance(Base):
    __tablename__ = "attendance"
 
    id          = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date        = Column(Date, nullable=False)
    status      = Column(String)                          
 
    employee    = relationship("Employee")


#Module-4
class ReviewCycle(Base):
    __tablename__ = "review_cycles"
 
    id          = Column(Integer, primary_key=True, index=True)
    period_name = Column(String)                          
    start_date  = Column(Date)
    end_date    = Column(Date)
    created_at  = Column(DateTime, default=func.now())
 
    reviews     = relationship("EmployeeReview", back_populates="cycle")


class EmployeeReview(Base):
    __tablename__ = "employee_reviews"
 
    id                  = Column(Integer, primary_key=True, index=True)
    cycle_id            = Column(Integer, ForeignKey("review_cycles.id"), nullable=False)
    employee_id         = Column(Integer, ForeignKey("employees.id"), nullable=False)
 
    self_achievements   = Column(Text, nullable=True)
    self_challenges     = Column(Text, nullable=True)
    self_goals          = Column(Text, nullable=True)
 
    manager_ratings     = Column(JSON, nullable=True)     
    manager_comments    = Column(Text, nullable=True)
 
    ai_summary          = Column(Text, nullable=True)     
    ai_flags            = Column(Text, nullable=True)     
    ai_development_actions = Column(JSON, nullable=True)  
 
    cycle               = relationship("ReviewCycle", back_populates="reviews")
    employee            = relationship("Employee")

#Module-5
class OnboardingChecklist(Base):
    __tablename__ = "onboarding_checklists"
 
    id      = Column(Integer, primary_key=True, index=True)
    role    = Column(String, nullable=False)              
    items   = Column(JSON, default=list)
 
 
class ChecklistProgress(Base):
    __tablename__ = "checklist_progress"
 
    id              = Column(Integer, primary_key=True, index=True)
    employee_id     = Column(Integer, ForeignKey("employees.id"), nullable=False)
    checklist_id    = Column(Integer, ForeignKey("onboarding_checklists.id"), nullable=False)
    completed_items = Column(JSON, default=list)
 
    employee        = relationship("Employee")
 
 
class PolicyDocument(Base):
    __tablename__ = "policy_documents"
 
    id              = Column(Integer, primary_key=True, index=True)
    filename        = Column(String)
    file_path       = Column(String)
    raw_text        = Column(Text)                        
    embedding_stored= Column(Boolean, default=False)     
    uploaded_at     = Column(DateTime, default=func.now())
 
 
class ChatLog(Base):
    __tablename__ = "chat_logs"
 
    id          = Column(Integer, primary_key=True, index=True)
    question    = Column(Text)
    answer      = Column(Text)
    created_at  = Column(DateTime, default=func.now())