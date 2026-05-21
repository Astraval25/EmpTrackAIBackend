from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class OrgCreate(BaseModel):
    name: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    password: str
    company_name: str = Field(..., alias="companyName")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class EmployeeCreate(BaseModel):
    name: str
    username: str
    password: str
    email: Optional[EmailStr] = None

class EmployeeResponse(BaseModel):
    username: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    created_by: str

class LogResponse(BaseModel):
    template: str
    activity: str
    timestamp: datetime

class LogListResponse(BaseModel):
    logs: list[LogResponse]
    total: int
    has_more: bool

class ActivityLogCreate(BaseModel):
    template: str
    log_data: dict
    ip_address: Optional[str] = None
    device_info: Optional[dict] = None