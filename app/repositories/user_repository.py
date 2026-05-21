from sqlalchemy.orm import Session
from app.models.user_model import User, Org, Employee
from uuid import UUID

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_org(self, name: str):
        org = Org(name=name)
        self.db.add(org)
        self.db.commit()
        self.db.refresh(org)
        return org

    def create_user(self, org_id: UUID, email: str, password_hash: str, name: str = None):
        user = User(org_id=org_id, email=email, password_hash=password_hash, name=name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_login(self, identifier: str):
        return (
            self.db.query(User)
            .filter((User.email == identifier) | (User.name == identifier))
            .first()
        )

    def create_employee(self, org_id: UUID, name: str, username: str, password_hash: str, email: str = None):
        employee = Employee(
            org_id=org_id,
            name=name,
            username=username,
            password_hash=password_hash,
            email=email
        )
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee