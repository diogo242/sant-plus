from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from backend.app.core.config import settings
from backend.app.core.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token
)
from backend.app.database import get_db
from backend.app.models.user import User, UserRole, RefreshToken
from backend.app.schemas.auth import Token, LoginRequest, TokenPayload

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email, User.is_active == True))
    return result.scalar_one_or_none()


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    from uuid import UUID
    result = await db.execute(select(User).where(User.id == UUID(user_id), User.is_active == True))
    return result.scalar_one_or_none()


async def require_user(current_user: Optional[User] = Depends(get_current_user)) -> User:
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non authentifié")
    return current_user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    user.last_login = datetime.utcnow()
    db.add(user)
    await db.commit()
    access = create_access_token({"sub": str(user.id), "role": user.role.value, "email": user.email})
    refresh = create_refresh_token({"sub": str(user.id), "email": user.email})
    return Token(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={"id": str(user.id), "email": user.email, "full_name": user.full_name, "role": user.role.value},
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str = Body(..., embed=True), db: AsyncSession = Depends(get_db)):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token invalide")
    user_id = payload.get("sub")
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token, RefreshToken.revoked == False))
    token_obj = result.scalar_one_or_none()
    if not token_obj or str(token_obj.user_id) != user_id:
        raise HTTPException(status_code=401, detail="Refresh token invalide ou révoqué")
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Utilisateur inactif")
    access = create_access_token({"sub": str(user.id), "role": user.role.value, "email": user.email})
    new_refresh = create_refresh_token({"sub": str(user.id), "email": user.email})
    token_obj.revoked = True
    db.add(token_obj)
    new_token_obj = RefreshToken(user_id=user.id, token=new_refresh, expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS))
    db.add(new_token_obj)
    await db.commit()
    return Token(
        access_token=access,
        refresh_token=new_refresh,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={"id": str(user.id), "email": user.email, "full_name": user.full_name, "role": user.role.value},
    )


from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "patient"
    phone: Optional[str] = None


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    try:
        role = UserRole(req.role)
    except ValueError:
        role = UserRole.PATIENT
    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        phone=req.phone,
        role=role,
        is_verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": str(user.id), "email": user.email, "full_name": user.full_name, "role": user.role.value}
