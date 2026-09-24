from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas import LoginRequest, ProfileUpdate, RegisterRequest


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def register(self, data: RegisterRequest) -> tuple[User, str]:
        existing = self.db.scalar(select(User).where(User.email == data.email.lower()))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        user = User(
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            name=data.name.strip(),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        token = create_access_token(user.id, extra={"email": user.email})
        return user, token

    def login(self, data: LoginRequest) -> tuple[User, str]:
        user = self.db.scalar(select(User).where(User.email == data.email.lower()))
        if user is None or not user.password_hash or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = create_access_token(user.id, extra={"email": user.email})
        return user, token

    def update_profile(self, user: User, data: ProfileUpdate) -> User:
        user.name = data.name.strip()
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
