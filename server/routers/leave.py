from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import json
import calendar

from database import get_db
from models import LeaveRequest, LeaveBalance, Attendance, Employee
from schemas import (
    LeaveRequestCreate, LeaveRequestResponse, LeaveApproval,
    LeaveBalanceResponse, AttendanceCreate, AttendanceResponse
)

router = APIRouter()

# Leave Balance


@router.post("/balances/initialize/{employee_id}")
def initialize_leave_balances(employee_id: int, db: Session = Depends(get_db)):
    """Initialize default leave balances for a new employee (4 types)."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    existing = db.query(LeaveBalance).filter(
        LeaveBalance.employee_id == employee_id).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Leave balances already initialized")

    defaults = [
        {"leave_type": "sick", "total": 12},
        {"leave_type": "casual", "total": 12},
        {"leave_type": "earned", "total": 15},
        {"leave_type": "wfh", "total": 52},
    ]
    for d in defaults:
        db.add(LeaveBalance(employee_id=employee_id,
               leave_type=d["leave_type"], total=d["total"], used=0))

    db.commit()
    return {"message": f"Leave balances initialized for employee {employee_id}"}


@router.get("/balances/{employee_id}", response_model=List[LeaveBalanceResponse])
def get_leave_balances(employee_id: int, db: Session = Depends(get_db)):
    """Get all leave balances for an employee."""
    balances = db.query(LeaveBalance).filter(
        LeaveBalance.employee_id == employee_id).all()
    if not balances:
        raise HTTPException(
            status_code=404, detail="No leave balances found. Initialize first.")
    return balances


# Leave Requests
@router.post("/requests", response_model=LeaveRequestResponse)
def apply_for_leave(leave: LeaveRequestCreate, db: Session = Depends(get_db)):
    """Employee applies for leave. Validates dates and checks balance."""
    employee = db.query(Employee).filter(
        Employee.id == leave.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if leave.start_date > leave.end_date:
        raise HTTPException(
            status_code=400, detail="Start date must be before or equal to end date")

    days_requested = (leave.end_date - leave.start_date).days + \
        1.  # Checking balance, both days so +1
    balance = db.query(LeaveBalance).filter(
        LeaveBalance.employee_id == leave.employee_id,
        LeaveBalance.leave_type == leave.leave_type
    ).first()

    if balance:
        remaining = balance.total - balance.used
        if days_requested > remaining:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient {leave.leave_type} leave. Remaining: {remaining}, Requested: {days_requested}"
            )

    db_leave = LeaveRequest(**leave.model_dump())
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave


@router.get("/requests", response_model=List[LeaveRequestResponse])
def list_leave_requests(
    employee_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List leave requests with optional employee/status filters."""
    query = db.query(LeaveRequest)
    if employee_id:
        query = query.filter(LeaveRequest.employee_id == employee_id)
    if status:
        query = query.filter(LeaveRequest.status == status)
    return query.order_by(LeaveRequest.created_at.desc()).all()


@router.patch("/requests/{request_id}/approve", response_model=LeaveRequestResponse)
def approve_or_reject_leave(request_id: int, approval: LeaveApproval, db: Session = Depends(get_db)):
    """Manager approves/rejects. On approval, deducts from leave balance."""
    leave_req = db.query(LeaveRequest).filter(
        LeaveRequest.id == request_id).first()
    if not leave_req:
        raise HTTPException(status_code=404, detail="Leave request not found")

    if leave_req.status != "pending":
        raise HTTPException(
            status_code=400, detail=f"Already {leave_req.status}")

    if approval.status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=400, detail="Status must be 'approved' or 'rejected'")

    leave_req.status = approval.status
    leave_req.manager_comment = approval.manager_comment

    # On approval → update balance
    if approval.status == "approved":
        days_used = (leave_req.end_date - leave_req.start_date).days + 1
        balance = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == leave_req.employee_id,
            LeaveBalance.leave_type == leave_req.leave_type
        ).first()

        if balance:
            balance.used += days_used
        else:
            db.add(LeaveBalance(
                employee_id=leave_req.employee_id,
                leave_type=leave_req.leave_type,
                total=12, used=days_used
            ))

    db.commit()
    db.refresh(leave_req)
    return leave_req


# Attendance endpoints
@router.post("/attendance", response_model=AttendanceResponse)
def mark_attendance(att: AttendanceCreate, db: Session = Depends(get_db)):
    if att.status not in ["present", "wfh", "half_day", "absent"]:  # Attendance marking
        raise HTTPException(
            status_code=400, detail="Status must be: present, wfh, half_day, or absent")

    existing = db.query(Attendance).filter(
        Attendance.employee_id == att.employee_id,
        Attendance.date == att.date
    ).first()

    if existing:
        existing.status = att.status
        db.commit()
        db.refresh(existing)
        return existing

    db_att = Attendance(**att.model_dump())
    db.add(db_att)
    db.commit()
    db.refresh(db_att)
    return db_att


@router.get("/attendance", response_model=List[AttendanceResponse])
def get_attendance(
    employee_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    # Getting attendance records with optional filter
    query = db.query(Attendance)
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    return query.order_by(Attendance.date.desc()).all()

# Calendar View


@router.get("/calendar")
def get_leave_calendar(
    year: int = Query(...),
    month: int = Query(...),
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Returns each day of the month with a list of employees on leave."""
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    query = db.query(LeaveRequest).join(Employee).filter(  # leaves overlapping with this month
        LeaveRequest.status == "approved",
        LeaveRequest.start_date <= last_day,
        LeaveRequest.end_date >= first_day
    )
    if department:
        query = query.filter(Employee.department == department)

    leaves = query.all()

    # Calendar build
    calendar_data = {}
    current = first_day
    while current <= last_day:
        on_leave = []
        for leave in leaves:
            if leave.start_date <= current <= leave.end_date:
                emp = db.query(Employee).filter(
                    Employee.id == leave.employee_id).first()
                on_leave.append({
                    "employee_id": leave.employee_id,
                    "name": emp.name if emp else "Unknown",
                    "leave_type": leave.leave_type
                })
        calendar_data[current.isoformat()] = on_leave
        current += timedelta(days=1)

    return {"year": year, "month": month, "calendar": calendar_data}

# Monthly Attendance summary


@router.get("/attendance/summary/{employee_id}")
def monthly_attendance_summary(
    employee_id: int,
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db)
):
    # Getting monthly summary
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    records = db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.date >= first_day,
        Attendance.date <= last_day
    ).all()

    summary = {"present": 0, "wfh": 0, "half_day": 0, "absent": 0}
    for r in records:
        if r.status in summary:
            summary[r.status] += 1

    working_days = 0
    current = first_day
    while current <= last_day:
        if current.weekday() < 5:
            working_days += 1
        current += timedelta(days=1)

    effective = summary["present"] + \
        summary["wfh"] + (summary["half_day"] * 0.5)
    att_pct = round((effective / working_days * 100),
                    1) if working_days > 0 else 0

    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "year": year, "month": month,
        "working_days": working_days,
        "summary": summary,
        "attendance_percentage": att_pct
    }

# Unusual leave pattern detection


@router.get("/ai/leave-patterns")
def detect_leave_patterns(department: Optional[str] = None, db: Session = Depends(get_db)):
    """
    AI flags unusual patterns like repeated Monday/Friday leaves.
    Pre-processes data with day-of-week info before sending to Gemini.
    """
    query = db.query(LeaveRequest).join(Employee).filter(
        LeaveRequest.status == "approved",
        Employee.is_active == True
    )
    if department:
        query = query.filter(Employee.department == department)

    leaves = query.all()
    if not leaves:
        return {"message": "No leave records to analyze", "unusual_patterns": [], "capacity_risks": []}

    # Expand each leave into individual dates with day names
    leave_data = []
    for leave in leaves:
        emp = db.query(Employee).filter(
            Employee.id == leave.employee_id).first()
        current = leave.start_date
        while current <= leave.end_date:
            leave_data.append({
                "employee": emp.name,
                "department": emp.department,
                "type": leave.leave_type,
                "date": current.isoformat(),
                "day": current.strftime("%A")
            })
            current += timedelta(days=1)

    from services.gemini_service import analyze_leave_patterns
    return analyze_leave_patterns(leave_data)
