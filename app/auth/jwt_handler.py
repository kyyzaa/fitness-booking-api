"""
JWT Handler
Mengelola pembuatan dan verifikasi JWT tokens
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# Konfigurasi JWT
SECRET_KEY = "fitness-booking-secret-key-change-in-production"  # Ganti dengan environment variable di production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi password dengan hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError as e:
        # Password terlalu panjang untuk bcrypt
        return False


def get_password_hash(password: str) -> str:
    """
    Hash password menggunakan bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
        
    Raises:
        ValueError: Jika password terlalu panjang (> 72 bytes)
    """
    # Validasi panjang password untuk bcrypt (max 72 bytes)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        raise ValueError("Password tidak boleh lebih dari 72 bytes")
    
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Membuat JWT access token
    
    Args:
        data: Dictionary berisi payload yang akan di-encode
        expires_delta: Durasi expired token (default: 30 menit)
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode dan verifikasi JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Payload dictionary jika valid, None jika tidak valid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
