from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr
from app.core.database import get_session
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    position: str
    department: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register_user(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Użytkownik już istnieje")

    new_user = User(
        email = payload.email,
        first_name = payload.first_name,
        last_name = payload.last_name,
        password_hash = hash_password(payload.password),
        position = payload.position,
        department = payload.department,
    )
    session.add(new_user)
    await session.commit()
    return {"message": "Użytkownik utworzony pomyślnie"}


@router.post("/login")
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nieprawidłowe dane logowania")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

