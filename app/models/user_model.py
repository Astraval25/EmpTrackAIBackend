import uuid

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

class Org(Base):
    __tablename__ = "org"
    
    org_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())

    users = relationship("User", back_populates="org")
    employees = relationship("Employee", back_populates="org")


class User(Base):
    __tablename__ = "user"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("org.org_id", ondelete="CASCADE"))
    name = Column(String(200))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    org = relationship("Org", back_populates="users")


class Employee(Base):
    __tablename__ = "employee"
    
    employee_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("org.org_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    username = Column(String(100), unique=True)
    password_hash = Column(String, nullable=False)
    email = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    org = relationship("Org", back_populates="employees")


class ActivityLog(Base):
    __tablename__ = "activity_log"
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employee.employee_id", ondelete="CASCADE"), nullable=False)
    template = Column(String(100))
    log_data = Column(JSONB, nullable=True)
    log_timestamp = Column(DateTime, nullable=False, default=func.now())
    ip_address = Column(String(45))
    device_info = Column(JSONB)

    employee = relationship("Employee")