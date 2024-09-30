from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils import hash_password, verify_password, create_access_token
from app.database import SessionLocal
from app.models import User
from datetime import timedelta
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str

# DB 세션 관리
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 회원가입 라우트
@router.post("/signup/")


async def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")
    
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "회원가입 성공", "user": new_user.username}

# 로그인 라우트
@router.post("/login/")
async def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="잘못된 사용자명 또는 비밀번호입니다.")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": db_user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}