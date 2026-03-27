from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from database import get_db
from models import ReviewCycle, EmployeeReview, Employee
from schemas import (
    ReviewCycleCreate, ReviewCycleResponse,
    SelfAssessmentSubmit, ManagerReviewSubmit, EmployeeReviewResponse
)

router = APIRouter()

# HR creates a review cycle


@router.post("/cycles", response_model=ReviewCycleResponse)
def create_review_cycle(cycle: ReviewCycleCreate, db: Session = Depends(get_db)):
    db_cycle = ReviewCycle(**cycle.model_dump())
    db.add(db_cycle)
    db.commit()
    db.refresh(db_cycle)
    return db_cycle


@router.get("/cycles", response_model=List[ReviewCycleResponse])
def list_review_cycles(db: Session = Depends(get_db)):
    return db.query(ReviewCycle).order_by(ReviewCycle.created_at.desc()).all()


@router.post("/cycles/{cycle_id}/add-employees")
def add_employees_to_cycle(
    cycle_id: int,
    employee_ids: List[int],  # JSON body: [1, 2, 3]
    db: Session = Depends(get_db)
):
    # HR selects employees
    cycle = db.query(ReviewCycle).filter(ReviewCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")

    added = []
    for emp_id in employee_ids:
        # Skip if already added
        exists = db.query(EmployeeReview).filter(
            EmployeeReview.cycle_id == cycle_id,
            EmployeeReview.employee_id == emp_id
        ).first()
        if exists:
            continue

        db.add(EmployeeReview(cycle_id=cycle_id,
               employee_id=emp_id, status="pending"))
        added.append(emp_id)

    db.commit()
    return {"message": f"Added {len(added)} employees to cycle", "added_ids": added}


@router.get("/cycles/{cycle_id}/reviews", response_model=List[EmployeeReviewResponse])
def list_reviews_in_cycle(cycle_id: int, db: Session = Depends(get_db)):
    # Getting all reviews for a cycle
    return db.query(EmployeeReview).filter(EmployeeReview.cycle_id == cycle_id).all()


@router.put("/reviews/{review_id}/self-assessment")
def submit_self_assessment(
    review_id: int,
    data: SelfAssessmentSubmit,
    db: Session = Depends(get_db)
):
   # Filling self assessment form
    review = db.query(EmployeeReview).filter(
        EmployeeReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.self_assessment = data.self_assessment
    review.self_rating = data.self_rating
    review.status = "self_done"
    db.commit()
    db.refresh(review)
    return {"message": "Self-assessment submitted", "review_id": review_id}


@router.put("/reviews/{review_id}/manager-review")
def submit_manager_review(
    review_id: int,
    data: ManagerReviewSubmit,
    db: Session = Depends(get_db)
):

    # Rating on 5 parameters, quality, delivery, communication, intiative and teamwork. Sending as JSON
    review = db.query(EmployeeReview).filter(
        EmployeeReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.manager_ratings = data.manager_ratings
    review.manager_comment = data.manager_comment
    review.status = "manager_done"
    db.commit()
    db.refresh(review)
    return {"message": "Manager review submitted", "review_id": review_id}


@router.post("/reviews/{review_id}/generate-summary")
def generate_ai_summary(review_id: int, db: Session = Depends(get_db)):
    review = db.query(EmployeeReview).filter(
        EmployeeReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if not review.self_assessment or not review.manager_ratings:
        raise HTTPException(
            status_code=400, detail="Both self-assessment and manager review must be submitted first")

    employee = db.query(Employee).filter(
        Employee.id == review.employee_id).first()

    from services.gemini_service import generate_review_summary
    result = generate_review_summary(
        employee_name=employee.name,
        self_assessment=review.self_assessment,
        self_rating=review.self_rating,
        manager_ratings=review.manager_ratings,
        manager_comment=review.manager_comment or ""
    )

    # Saving ai outputs
    review.ai_summary = result.get("summary", "")
    review.ai_flags = json.dumps(result.get("flags", []))
    review.ai_development_actions = json.dumps(
        result.get("development_actions", []))
    review.status = "completed"
    db.commit()

    return {
        "review_id": review_id,
        "employee": employee.name,
        "summary": result.get("summary"),
        "flags": result.get("flags"),
        "development_actions": result.get("development_actions")
    }

# Getting single review with all data


@router.get("/reviews/{review_id}", response_model=EmployeeReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(EmployeeReview).filter(
        EmployeeReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("/reviews/{review_id}/export-pdf")
def export_review_pdf(review_id: int, db: Session = Depends(get_db)):
    review = db.query(EmployeeReview).filter(
        EmployeeReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    employee = db.query(Employee).filter(
        Employee.id == review.employee_id).first()
    cycle = db.query(ReviewCycle).filter(
        ReviewCycle.id == review.cycle_id).first()

    # JSON parsing
    flags = json.loads(review.ai_flags) if review.ai_flags else []
    actions = json.loads(
        review.ai_development_actions) if review.ai_development_actions else []
    ratings = review.manager_ratings or {}

    # Returning in json format — frontend renders and prints as PDF (not added other pdf downloaders)
    return {
        "employee_name": employee.name,
        "designation": employee.designation,
        "department": employee.department,
        "review_period": cycle.period_name if cycle else "N/A",
        "self_assessment": review.self_assessment,
        "self_rating": review.self_rating,
        "manager_ratings": ratings,
        "manager_comment": review.manager_comment,
        "ai_summary": review.ai_summary,
        "ai_flags": flags,
        "development_actions": actions,
        "generated_at": datetime.utcnow().isoformat()
    }
