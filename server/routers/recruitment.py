from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import os

from database import get_db
from models import JobPosting, Candidate
from schemas import (
    JobPostingCreate, JobPostingResponse,
    CandidateCreate, CandidateResponse, CandidateStageUpdate
)

router = APIRouter()


@router.post("/jobs", response_model=JobPostingResponse)
def create_job_posting(job: JobPostingCreate, db: Session = Depends(get_db)):
    db_job = JobPosting(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/jobs", response_model=List[JobPostingResponse])
def list_job_postings(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(JobPosting)
    if status:
        query = query.filter(JobPosting.status == status)
    return query.order_by(JobPosting.created_at.desc()).all()


@router.get("/jobs/{job_id}", response_model=JobPostingResponse)
def get_job_posting(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job


@router.put("/jobs/{job_id}", response_model=JobPostingResponse)
def update_job_posting(job_id: int, job_update: JobPostingCreate, db: Session = Depends(get_db)):

    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    for key, value in job_update.model_dump().items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return job


@router.patch("/jobs/{job_id}/status")
def update_job_status(
    job_id: int,
    status: str = Query(..., description="open, closed, or filled"),
    db: Session = Depends(get_db)
):

    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    if status not in ["open", "closed", "filled"]:
        raise HTTPException(
            status_code=400, detail="Status must be: open, closed, or filled")

    job.status = status
    db.commit()
    return {"message": f"Job status updated to '{status}'"}

# Candidate endpoints


@router.post("/jobs/{job_id}/candidates", response_model=CandidateResponse)
def add_candidate(
    job_id: int,
    candidate: CandidateCreate,
    db: Session = Depends(get_db)
):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    db_candidate = Candidate(
        job_id=job_id,
        name=candidate.name,
        email=candidate.email
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


@router.get("/jobs/{job_id}/candidates", response_model=List[CandidateResponse])
def list_candidates(job_id: int, stage: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Candidate).filter(Candidate.job_id == job_id)
    if stage:
        query = query.filter(Candidate.stage == stage)

    return query.order_by(Candidate.created_at.desc()).all()


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.post("/candidates/{candidate_id}/upload-resume")
async def upload_resume(
    candidate_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Only PDF files are accepted"
        )

    safe_name = candidate.name.replace(" ", "_").lower()
    filename = f"{candidate_id}_{safe_name}_{file.filename}"
    file_path = f"uploads/resumes/{filename}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    candidate.resume_path = file_path
    db.commit()

    return {
        "message": "Resume uploaded successfully",
        "file_path": file_path,
        "candidate_id": candidate_id
    }


@router.patch("/candidates/{candidate_id}/stage", response_model=CandidateResponse)
def update_candidate_stage(
    candidate_id: int,
    stage_update: CandidateStageUpdate,
    db: Session = Depends(get_db)
):

    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    valid_stages = ["applied", "screening",
                    "interview", "offer", "hired", "rejected"]

    if stage_update.stage not in valid_stages:
        raise HTTPException(
            status_code=400, detail=f"Invalid stage. Musr be one of: {', '.join(valid_stages)}")

    candidate.stage = stage_update.stage
    db.commit()
    db.refresh(candidate)
    return candidate


@router.post("/candidates/{candidate_id}/analyze")
def analyze_candidate_resume(candidate_id: int, db: Session = Depends(get_db)):

    # Verifying candidate exists
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if candidate.resume_path is None:
        raise HTTPException(
            status_code=400, detail="No resume uploaded for this candidate. Upload a resume first.")

    if not os.path.exists(candidate.resume_path):
        raise HTTPException(
            status_code=404, detail="Resume file not found on server")

    # Fetching the job posting to compare with JD
    job = db.query(JobPosting).filter(
        JobPosting.id == candidate.job_id).first()
    if not job:
        raise HTTPException(
            status_code=404, detail="Associated job posting not found")

    # Extracting text from PDF
    from pypdf import PdfReader

    try:
        reader = PdfReader(candidate.resume_path)
        resume_text = ""
        for page in reader.pages:
            resume_text += page.extract_text() or ""

        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF. The file may be image-based or corrupted."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading PDF: {str(e)}")

    # Sending to Gemini for analysis
    from services.gemini_service import analyze_resume

    ai_result = analyze_resume(
        resume_text=resume_text,
        job_description=job.description,
        required_skills=job.required_skills
    )

    # Storing the generated data in db
    candidate.match_score = ai_result.get("match_score", 0)
    candidate.strengths = json.dumps(ai_result.get("strengths", []))
    candidate.gaps = json.dumps(ai_result.get("gaps", []))
    candidate.interview_questions = json.dumps(
        ai_result.get("interview_questions", []))
    candidate.ai_summary = ai_result.get("summary", "")

    db.commit()
    db.refresh(candidate)

    # Result
    return {
        "candidate_id": candidate_id,
        "candidate_name": candidate.name,
        "job_role": job.role,
        "match_score": ai_result.get("match_score", 0),
        "strengths": ai_result.get("strengths", []),
        "gaps": ai_result.get("gaps", []),
        "interview_questions": ai_result.get("interview_questions", []),
        "summary": ai_result.get("summary", "")
    }

# Candidate Comparison Endpoint


@router.get("/jobs/{job_id}/compare")
def compare_candidates(
    job_id: int,
    candidate_ids: str = Query(
        ...,
        description="Comma-separated candidate IDs to compare, e.g., '1,2,3'"
    ),
    db: Session = Depends(get_db)
):
    # Parsing comma-separated IDs
    try:
        ids = [int(id.strip()) for id in candidate_ids.split(",")]
    except ValueError:
        raise HTTPException(
            status_code=400, detail="candidate_ids must be comma-separated integers")

    if len(ids) < 2:
        raise HTTPException(
            status_code=400, detail="Please provide at least 2 candidate IDs to compare")

    # Fetching all requested candidates
    candidates = db.query(Candidate).filter(
        Candidate.id.in_(ids),
        Candidate.job_id == job_id
    ).all()

    if len(candidates) < 2:
        raise HTTPException(
            status_code=404, detail="Could not find enough candidates to compare")

    comparison = []
    for c in candidates:
        comparison.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "stage": c.stage,
            "match_score": c.match_score,
            "strengths": json.loads(c.strengths) if c.strengths else [],
            "gaps": json.loads(c.gaps) if c.gaps else [],
            "interview_questions": json.loads(c.interview_questions) if c.interview_questions else [],
            "ai_summary": c.ai_summary
        })

    # Sorting by match score,
    comparison.sort(key=lambda x: x["match_score"] or 0, reverse=True)

    return {
        "job_id": job_id,
        "candidates_compared": len(comparison),
        "comparison": comparison
    }


@router.get("/jobs/{job_id}/pipeline")
def get_pipeline_summary(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    stages = ["applied", "screening",
              "interview", "offer", "hired", "rejected"]
    pipeline = {}

    for stage in stages:
        count = db.query(Candidate).filter(
            Candidate.job_id == job_id,
            Candidate.stage == stage
        ).count()
        pipeline[stage] = count

    return {
        "job_id": job_id,
        "job_role": job.role,
        "total_candidates": sum(pipeline.values()),
        "pipeline": pipeline
    }
