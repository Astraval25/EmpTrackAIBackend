from typing import Annotated, Any, Optional
from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID
from datetime import datetime

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
    model_config = ConfigDict(populate_by_name=True)

    identifier: Annotated[str, Field(validation_alias=AliasChoices("email", "username", "identifier", "kioskUsername"))]
    password: Annotated[str, Field(validation_alias=AliasChoices("password", "kioskPassword"))]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class EmployeeCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: Annotated[str, Field(validation_alias=AliasChoices("name", "employeeName"))]
    username: Annotated[str, Field(validation_alias=AliasChoices("username", "kioskUsername"))]
    password: Annotated[str, Field(validation_alias=AliasChoices("password", "kioskPassword"))]
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
    model_config = ConfigDict(populate_by_name=True)

    template: str
    log_data: Annotated[dict[str, Any], Field(validation_alias=AliasChoices("log_data", "logData"))]
    ip_address: Annotated[Optional[str], Field(validation_alias=AliasChoices("ip_address", "ipAddress"))] = None
    device_info: Annotated[Optional[dict[str, Any]], Field(validation_alias=AliasChoices("device_info", "deviceInfo"))] = None
