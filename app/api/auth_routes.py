"""
API Routes untuk Authentication
Endpoint untuk login, register, dan manajemen user
"""

import uuid
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.auth.jwt_handler import (ACCESS_TOKEN_EXPIRE_MINUTES,
                                  create_access_token, decode_access_token,
                                  get_password_hash, verify_password)
from app.domain.entities import User, UserRole
from app.infrastructure.repository import (InMemoryUserRepository,
                                           IUserRepository)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme untuk mendapatkan token dari header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Request/Response DTOs
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.CLIENT

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123",
                "role": "CLIENT",
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    role: str
    is_active: bool

    @classmethod
    def from_entity(cls, user: User):
        return cls(
            user_id=user.user_id,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
        )


# Dependency injection untuk repository
def get_user_repository() -> IUserRepository:
    from app.main import user_repository

    return user_repository


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(
    request: RegisterRequest, user_repo: IUserRepository = Depends(get_user_repository)
):
    """
    Registrasi user baru

    - **email**: Email user (harus unique)
    - **password**: Password (minimal 6 karakter, maksimal 72 karakter)
    - **role**: Role user (CLIENT, TRAINER, atau ADMIN)
    """
    # Validasi password length
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password minimal 6 karakter",
        )

    # Bcrypt limit: 72 bytes max
    password_bytes = request.password.encode("utf-8")
    if len(password_bytes) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password terlalu panjang ({len(password_bytes)} bytes). Maksimal 72 bytes",
        )

    # Cek apakah email sudah terdaftar
    existing_user = user_repo.find_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email sudah terdaftar"
        )

    try:
        # Hash password
        hashed_password = get_password_hash(request.password)

        # Buat user baru
        user = User(
            user_id=f"USR{uuid.uuid4().hex[:8].upper()}",
            email=request.email,
            hashed_password=hashed_password,
            role=request.role,
            is_active=True,
        )

        # Simpan user
        user_repo.save(user)

        return UserResponse.from_entity(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membuat user: {str(e)}",
        )


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """
    Login user dan mendapatkan JWT token

    - **username**: Email user
    - **password**: Password user

    Returns JWT access token yang valid untuk 30 menit
    """
    try:
        # Cari user berdasarkan email (username di form adalah email)
        user = user_repo.find_by_email(form_data.username)

        # Validasi user dan password
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email atau password salah",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Cek apakah user aktif
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User tidak aktif"
            )

        # Buat access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.user_id, "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires,
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            email=user.email,
            role=user.role.value,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    token: str = Depends(oauth2_scheme),
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """
    Mendapatkan informasi user yang sedang login

    Memerlukan JWT token di header: Authorization: Bearer <token>
    """
    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Ambil user_id dari payload
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Cari user
    user = user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan"
        )

    return UserResponse.from_entity(user)
