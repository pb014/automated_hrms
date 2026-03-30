from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime

from database import get_db
from models import Employee, JobPosting, Candidate, LeaveBalance, LeaveRequest

router = APIRouter()


@router.get("/headcount")
def headcount_by_department(db: Session = Depends(get_db)):

    results = db.query(
        Employee.department, func.count(Employee.id)
    ).filter(Employee.is_active == True).group_by(Employee.department).all()

    return {
        "total": sum(count for _, count in results),
        "by_department": [{"department": dept, "count": count} for dept, count in results]
    }


@router.get("/attrition")
def attrition_rate(db: Session = Depends(get_db)):
    # using formula for attrition rate
    total = db.query(Employee).count()
    terminated = db.query(Employee).filter(
        Employee.termination_date.isnot(None)).count()
    active = db.query(Employee).filter(Employee.is_active == True).count()

    rate = round((terminated / total * 100), 1) if total > 0 else 0
    return {"total": total, "active": active, "terminated": terminated, "attrition_rate_pct": rate}


@router.get("/tenure")
def average_tenure_by_department(db: Session = Depends(get_db)):

    employees = db.query(Employee).filter(Employee.is_active == True).all()
    today = date.today()

    dept_tenures = {}
    for emp in employees:
        days = (today - emp.joining_date).days
        dept_tenures.setdefault(emp.department, []).append(days)

    result = []
    for dept, tenures in dept_tenures.items():
        avg_days = sum(tenures) / len(tenures)
        result.append({
            "department": dept,
            "avg_tenure_days": round(avg_days),
            "avg_tenure_months": round(avg_days / 30, 1),
            "employee_count": len(tenures)
        })

    return sorted(result, key=lambda x: x["avg_tenure_days"], reverse=True)


@router.get("/positions")
def open_vs_filled_positions(db: Session = Depends(get_db)):

    open_count = db.query(JobPosting).filter(
        JobPosting.status == "open").count()
    filled_count = db.query(JobPosting).filter(
        JobPosting.status == "filled").count()
    closed_count = db.query(JobPosting).filter(
        JobPosting.status == "closed").count()

    hired = db.query(Candidate).filter(Candidate.stage == "hired").count()

    return {
        "open_positions": open_count,
        "filled_positions": filled_count,
        "closed_positions": closed_count,
        "total_hired_candidates": hired
    }


@router.get("/leave-utilisation")
def leave_utilisation(db: Session = Depends(get_db)):
    balances = db.query(LeaveBalance).all()

    by_type = {}
    for b in balances:
        entry = by_type.setdefault(b.leave_type, {"total": 0, "used": 0})
        entry["total"] += b.total
        entry["used"] += b.used

    result = []
    for lt, data in by_type.items():
        rate = round((data["used"] / data["total"] * 100),
                     1) if data["total"] > 0 else 0
        result.append({
            "leave_type": lt,
            "total_allocated": data["total"],
            "total_used": data["used"],
            "utilisation_pct": rate
        })

    return result


@router.get("/ai/monthly-summary")
def ai_monthly_summary(db: Session = Depends(get_db)):
    # We use realtime data and feed it to AI to prevent hallucination
    total_emp = db.query(Employee).filter(Employee.is_active == True).count()
    terminated = db.query(Employee).filter(
        Employee.termination_date.isnot(None)).count()
    open_jobs = db.query(JobPosting).filter(
        JobPosting.status == "open").count()
    filled_jobs = db.query(JobPosting).filter(
        JobPosting.status == "filled").count()
    pending_leaves = db.query(LeaveRequest).filter(
        LeaveRequest.status == "pending").count()

    dept_counts = db.query(
        Employee.department, func.count(Employee.id)
    ).filter(Employee.is_active == True).group_by(Employee.department).all()

    analytics_data = {
        "total_active_employees": total_emp,
        "terminated_employees": terminated,
        "attrition_rate": round((terminated / (total_emp + terminated) * 100), 1) if (total_emp + terminated) > 0 else 0,
        "open_positions": open_jobs,
        "filled_positions": filled_jobs,
        "pending_leave_requests": pending_leaves,
        "headcount_by_department": {dept: count for dept, count in dept_counts},
        "report_date": datetime.utcnow().strftime("%B %Y")
    }

    from services.gemini_service import generate_hr_summary
    summary = generate_hr_summary(analytics_data)

    return {"data": analytics_data, "ai_summary": summary}
