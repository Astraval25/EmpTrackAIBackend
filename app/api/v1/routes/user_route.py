import json
from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, cast, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_employee, get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user_model import ActivityLog, Employee, User as AdminUser
from app.schemas.user_schema import (
    ActivityLogCreate,
    EmployeeCreate,
    EmployeeResponse,
    LogListResponse,
    LogResponse,
    RegisterRequest,
    Token,
    UserLogin,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["Users"])

@router.post("/register", response_model=dict)
def register(register_request: RegisterRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.register_org_and_admin(
        company_name=register_request.company_name,
        admin_name=register_request.email,
        email=register_request.email,
        password=register_request.password,
    )
    return {"message": "Organization and Admin registered successfully", "user_id": str(user.user_id)}

@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.repo.get_user_by_email(login_data.identifier)
    if user and verify_password(login_data.password, user.password_hash):
        token = create_access_token(
            {
                "sub": user.email,
                "user_id": str(user.user_id),
                "org_id": str(user.org_id),
                "role": "admin",
            }
        )
        return {
            "token": token,
            "role": "admin",
            "companyName": user.org.name if user.org is not None else "",
        }

    employee = service.repo.get_employee_by_username(login_data.identifier)
    if employee and verify_password(login_data.password, employee.password_hash):
        token = create_access_token(
            {
                "sub": employee.username,
                "employee_id": str(employee.employee_id),
                "org_id": str(employee.org_id),
                "role": "employee",
            }
        )
        return {
            "token": token,
            "role": "employee",
            "companyName": employee.org.name if employee.org is not None else "",
            "employeeName": employee.name,
            "username": employee.username,
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )

@router.get("/users", response_model=list[EmployeeResponse])
def get_users(
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    employees = (
        db.query(Employee)
        .filter(Employee.org_id == current_user.org_id)
        .order_by(Employee.username)
        .all()
    )
    return [
        EmployeeResponse(
            username=e.username,
            name=e.name,
            email=e.email,
            created_by=current_user.name or current_user.email,
        )
        for e in employees
    ]

@router.post("/users", response_model=dict)
def create_user(
    employee_in: EmployeeCreate,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    password_hash = hash_password(employee_in.password)
    service = UserService(db)
    try:
        employee = service.repo.create_employee(
            org_id=current_user.org_id,
            name=employee_in.name,
            username=employee_in.username,
            password_hash=password_hash,
            email=employee_in.email,
        )
    except IntegrityError as err:
        db.rollback()
        if "unique constraint" in str(err).lower() or "duplicate" in str(err).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error",
        )

    return {"message": "User created", "user_id": str(employee.employee_id)}


@router.post("/logs", response_model=dict)
def create_log(
    log_in: ActivityLogCreate,
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    log = service.repo.create_activity_log(
        employee_id=current_employee.employee_id,
        template=log_in.template,
        log_data=log_in.log_data,
        ip_address=log_in.ip_address,
        device_info=log_in.device_info,
    )
    return {
        "message": "Log created",
        "log_id": str(log.log_id),
        "employeeName": current_employee.name,
        "username": current_employee.username,
    }

@router.get("/users/{username}/logs", response_model=LogListResponse)
def get_logs(
    username: str,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    employee = (
        db.query(Employee)
        .filter(Employee.org_id == current_user.org_id, Employee.username == username)
        .first()
    )
    if employee is None:
        return LogListResponse(logs=[], total=0, has_more=False)

    logs_query = db.query(ActivityLog).filter(ActivityLog.employee_id == employee.employee_id)

    if search:
        logs_query = logs_query.filter(
            or_(
                ActivityLog.template.ilike(f"%{search}%"),
                cast(ActivityLog.log_data, String).ilike(f"%{search}%"),
            )
        )

    if start_date is not None:
        logs_query = logs_query.filter(
            ActivityLog.log_timestamp >= datetime.combine(start_date, datetime.min.time())
        )

    if end_date is not None:
        logs_query = logs_query.filter(
            ActivityLog.log_timestamp < datetime.combine(end_date + timedelta(days=1), datetime.min.time())
        )

    total = logs_query.count()
    logs = (
        logs_query.order_by(ActivityLog.log_timestamp.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    log_items = [
        LogResponse(
            template=log.template,
            activity=json.dumps(log.log_data) if log.log_data is not None else "",
            timestamp=log.log_timestamp,
        )
        for log in logs
    ]

    return LogListResponse(
        logs=log_items,
        total=total,
        has_more=offset + len(log_items) < total,
    )
