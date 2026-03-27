from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import (
    OnboardingChecklist, ChecklistProgress, PolicyDocument,
    ChatLog, Employee
)
from schemas import (
    ChecklistCreate, ChecklistResponse, ChatRequest, ChatResponse, ChatLogResponse, PolicyDocumentResponse
)

router = APIRouter()


# Checklist

@router.post("/checklists", response_model=ChecklistResponse)
def create_checklist(checklist: ChecklistCreate, db: Session = Depends(get_db)):
    db_checklist = OnboardingChecklist(**checklist.model_dump())
    db.add(db_checklist)
    db.commit()
    db.refresh(db_checklist)
    return db_checklist


@router.get("/checklists", response_model=List[ChecklistResponse])
def list_checklists(role: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(OnboardingChecklist)
    if role:
        query = query.filter(OnboardingChecklist.role == role)
    return query.all()


# Progress Tracking

@router.post("/progress/{employee_id}/{checklist_id}")
def assign_checklist(employee_id: int, checklist_id: int, db: Session = Depends(get_db)):
    # Assigning checklist to new joiner
    existing = db.query(ChecklistProgress).filter(
        ChecklistProgress.employee_id == employee_id,
        ChecklistProgress.checklist_id == checklist_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Checklist already assigned")

    progress = ChecklistProgress(
        employee_id=employee_id, checklist_id=checklist_id, completed_items=[]
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return {"message": "Checklist assigned", "progress_id": progress.id}


@router.get("/progress/{employee_id}")
def get_employee_progress(employee_id: int, db: Session = Depends(get_db)):
    # Shows completion progress for an employee
    records = db.query(ChecklistProgress).filter(
        ChecklistProgress.employee_id == employee_id
    ).all()

    result = []
    for p in records:
        checklist = db.query(OnboardingChecklist).filter(
            OnboardingChecklist.id == p.checklist_id
        ).first()
        total = len(checklist.items) if checklist and checklist.items else 0
        completed = len(p.completed_items) if p.completed_items else 0
        result.append({
            "progress_id": p.id,
            "checklist_id": p.checklist_id,
            "role": checklist.role if checklist else "Unknown",
            "total_items": total,
            "completed": completed,
            "percentage": round((completed / total * 100), 1) if total > 0 else 0,
            "items": checklist.items if checklist else [],
            "completed_items": p.completed_items or []
        })
    return result


@router.patch("/progress/{progress_id}/complete-item")
def complete_checklist_item(progress_id: int, item_index: int, db: Session = Depends(get_db)):
    # Mark a checklist item as complete
    progress = db.query(ChecklistProgress).filter(
        ChecklistProgress.id == progress_id).first()
    if not progress:
        raise HTTPException(
            status_code=404, detail="Progress record not found")

    completed = progress.completed_items or []
    if item_index not in completed:
        completed.append(item_index)
        progress.completed_items = completed
        db.commit()

    return {"message": f"Item {item_index} marked complete", "completed_items": completed}


# Policy Document Upload

@router.post("/policies", response_model=PolicyDocumentResponse)
async def upload_policy(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Policy PDF upload for RAG, chatbot will respond according to divided chunks of this document
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")

    file_path = f"uploads/policies/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    from pypdf import PdfReader
    try:
        reader = PdfReader(file_path)
        raw_text = ""
        for page in reader.pages:
            raw_text += (page.extract_text() or "") + "\n"
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read PDF: {str(e)}")

    from services.rag_service import add_to_index
    chunks_added = add_to_index(raw_text)

    doc = PolicyDocument(
        filename=file.filename, file_path=file_path,
        raw_text=raw_text, embedding_stored=True
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


@router.get("/policies", response_model=List[PolicyDocumentResponse])
def list_policies(db: Session = Depends(get_db)):
    return db.query(PolicyDocument).all()


# RAG powered AI Chatbot

@router.post("/chat", response_model=ChatResponse)
def ask_chatbot(req: ChatRequest, db: Session = Depends(get_db)):
    # Chatbot will respond according to the policies uploaded by HR

    from services.rag_service import search
    relevant_chunks = search(req.question, top_k=3)

    # sending to gemini
    from services.gemini_service import answer_policy_question
    result = answer_policy_question(req.question, relevant_chunks)

    log = ChatLog(
        employee_id=req.employee_id,
        question=req.question,
        answer=result["answer"],
        could_answer=result["could_answer"]
    )
    db.add(log)
    db.commit()

    return ChatResponse(answer=result["answer"], could_answer=result["could_answer"])


# Chat Logs for HR

@router.get("/chat-logs", response_model=List[ChatLogResponse])
def get_chat_logs(db: Session = Depends(get_db)):
    return db.query(ChatLog).order_by(ChatLog.created_at.desc()).all()


@router.get("/chat-logs/top-questions")
def get_top_questions(db: Session = Depends(get_db)):
    # Which questions are most asked, for HR
    logs = db.query(ChatLog.question, func.count(ChatLog.id).label("count")).group_by(
        ChatLog.question
    ).order_by(func.count(ChatLog.id).desc()).limit(10).all()

    return [{"question": q, "times_asked": c} for q, c in logs]
