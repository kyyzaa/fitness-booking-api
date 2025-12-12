"""
Authentication Dependencies
Dependencies untuk protect routes dengan JWT authentication
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.domain.entities import User, UserRole
from app.infrastructure.repository import IUserRepository
from app.auth.jwt_handler import decode_access_token

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_user_repository() -> IUserRepository:
    """Get user repository instance"""
    from app.main import user_repository
    return user_repository


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: IUserRepository = Depends(get_user_repository)
) -> User:
    """
    Dependency untuk mendapatkan user yang sedang login dari JWT token
    
    Digunakan untuk protect routes yang memerlukan autentikasi
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
    
    # Ambil user_id dari payload
    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception
    
    # Cari user
    user = user_repo.find_by_id(user_id)
    if not user:
        raise credentials_exception
    
    # Cek apakah user aktif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency untuk memastikan user aktif
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def require_role(required_role: UserRole):
    """
    Factory function untuk membuat dependency yang memeriksa role user
    
    Usage:
        @router.get("/admin-only")
        def admin_endpoint(user: User = Depends(require_role(UserRole.ADMIN))):
            ...
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden. Required role: {required_role.value}"
            )
        return current_user
    
    return role_checker


async def get_current_client(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency untuk memastikan user adalah CLIENT
    """
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to clients only"
        )
    return current_user


async def get_current_trainer(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency untuk memastikan user adalah TRAINER
    """
    if current_user.role != UserRole.TRAINER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to trainers only"
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency untuk memastikan user adalah ADMIN
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to admins only"
        )
    return current_user
