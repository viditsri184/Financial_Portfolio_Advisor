from fastapi import APIRouter, HTTPException
from backend.db.sqlite import SessionLocal
from backend.db.models import User
from backend.utils.security import hash_password, verify_password
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(email: str, password: str):
    db = SessionLocal()
    exists = db.query(User).filter_by(email=email).first()
    if exists:
        raise HTTPException(400, "Email already registered")

    user = User(
        user_id=str(uuid.uuid4()),
        email=email,
        password_hash=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.close()

    return {"message": "Registration successful"}

@router.post("/login")
def login(email: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    return {"user_id": user.user_id}
