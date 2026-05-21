from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password
from uuid import UUID

class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register_org_and_admin(self, company_name: str, admin_name: str, email: str, password: str):
        org = self.repo.create_org(company_name)
        hashed_pw = hash_password(password)
        user = self.repo.create_user(org.org_id, email, hashed_pw, admin_name)
        return user