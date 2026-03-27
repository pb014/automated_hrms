from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
import csv
import io
from fastapi.responses import StreamingResponse

from database import get_db
from models import Employee, Document
from schemas import(
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    EmployeeListResponse, DocumentResponse
)

router = APIRouter()

@router.post("/", response_model=EmployeeResponse)
def createEmployee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    existing = db.query(Employee).filter(Employee.email == employee.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    return db_employee

@router.get("/", response_model=List[EmployeeListResponse])
def list_employees(
    department: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Employee)
    
    if department:
        query = query.filter(Employee.department == department)
    
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Employee.name.ilike(search_term),
                Employee.email.ilike(search_term),
                Employee.designation.ilike(search_term),
                Employee.department.ilike(search_term),
            )
        )
    
    return query.offset(skip).limit(limit).all()


@router.get("/departments", response_model=List[str])
def get_departments(db: Session= Depends(get_db)):
    results = db.query(Employee.department).distinct().all()
    return [r[0] for r in results if r[0]]


@router.get("/org-chart")
def get_org_chart(db: Session = Depends(get_db)):
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    
    emp_dict = {}
    for emp in employees:
        emp_dict[emp.id] = {
            "id": emp.id,
            "name": emp.name,
            "designation": emp.designation,
            "department": emp.department,
            "manager_id": emp.manager_id,
            "children": []
        }
    
    
    roots = []  
    for emp_id, emp_data in emp_dict.items():
        if emp_data["manager_id"] and emp_data["manager_id"] in emp_dict:
            emp_dict[emp_data["manager_id"]]["children"].append(emp_data)
        else:
            roots.append(emp_data)
    
    return roots


@router.get("/export-csv")
def export_csv(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "ID", "Name", "Email", "Designation", "Department",
        "Joining Date", "Contact", "Manager ID", "Active"
    ])
    
    for emp in employees:
        writer.writerow([
            emp.id, emp.name, emp.email, emp.designation, emp.department,
            emp.joining_date, emp.contact, emp.manager_id, emp.is_active
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees.csv"}
    )
 
@router.get("/duplicates")
def check_duplicates(db: Session = Depends(get_db)):
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    
    duplicates = []
    incomplete = []
    
    seen = {}
    for emp in employees:
        key = (emp.name.lower().strip(), emp.department.lower().strip())
        if key in seen:
            duplicates.append({
                "employee_1": {"id": seen[key].id, "name": seen[key].name},
                "employee_2": {"id": emp.id, "name": emp.name},
                "reason": f"Same name and department: {emp.department}"
            })
        else:
            seen[key] = emp
    

    for emp in employees:
        missing = []
        if emp.contact is None:
            missing.append("contact")
        if emp.manager_id is None:
            missing.append("manager")
        if emp.bio is None:
            missing.append("bio (not AI-generated yet)")
        
        if missing:
            incomplete.append({
                "id": emp.id,
                "name": emp.name,
                "missing_fields": missing
            })
    
    return {
        "duplicates": duplicates,
        "incomplete": incomplete,
        "total_flagged": len(duplicates) + len(incomplete)
    }


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):

    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    update_data = employee_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(employee, key, value)
    
    db.commit()
    db.refresh(employee)
    return employee

@router.delete("/{employee_id}")
def deactivate_employee(employee_id: int, db: Session = Depends(get_db)):
    
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee.is_active = False
    employee.termination_date = func.now().date()
    db.commit()
    
    return {"message": f"Employee {employee.name} deactivated successfully"}

#Document upload endpoints
@router.post("/{employee_id}/documents", response_model=DocumentResponse)
async def upload_document(
    employee_id: int,
    doc_type: str = Query(..., description="Type: offer_letter, id_proof, etc."),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    file_path = f"uploads/documents/{employee_id}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    doc = Document(
        employee_id=employee_id,
        filename=file.filename,
        file_path=file_path,
        doc_type=doc_type
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    return doc


@router.get("/{employee_id}/documents", response_model=List[DocumentResponse])
def get_employee_documents(employee_id: int, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.employee_id == employee_id).all()


@router.post("/{employee_id}/generate-bio")
def generate_bio(employee_id: int, db: Session = Depends(get_db)):

    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    from services.gemini_service import generate_employee_bio
    
    bio = generate_employee_bio(
        name=str(employee.name),
        designation=str(employee.designation),
        department=str(employee.department),
        joining_date=str(employee.joining_date),
        contact=str(employee.contact)
    )
    

    employee.bio = bio
    db.commit()
    db.refresh(employee)
    
    return {"bio": bio, "employee_id": employee_id}