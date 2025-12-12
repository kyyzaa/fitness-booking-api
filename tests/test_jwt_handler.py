"""
Unit tests untuk JWT Handler
Test coverage: token creation, validation, password hashing
"""
import pytest
from datetime import timedelta
from app.auth.jwt_handler import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
    SECRET_KEY,
    ALGORITHM
)
from jose import jwt


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_get_password_hash_creates_hash(self):
        """Test bahwa password di-hash dengan benar"""
        password = "password123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")
    
    def test_get_password_hash_different_for_same_password(self):
        """Test bahwa hash berbeda untuk password yang sama (salt random)"""
        password = "password123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2  # Salt makes them different
    
    def test_get_password_hash_raises_error_for_long_password(self):
        """Test error untuk password > 72 bytes"""
        long_password = "a" * 73
        with pytest.raises(ValueError) as exc_info:
            get_password_hash(long_password)
        assert "72 bytes" in str(exc_info.value)
    
    def test_verify_password_correct(self):
        """Test verifikasi password yang benar"""
        password = "password123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test verifikasi password yang salah"""
        password = "password123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty(self):
        """Test verifikasi password kosong"""
        password = "password123"
        hashed = get_password_hash(password)
        assert verify_password("", hashed) is False
    
    def test_verify_password_with_long_password_returns_false(self):
        """Test verifikasi dengan password terlalu panjang returns False"""
        password = "a" * 73
        hashed = get_password_hash("short")
        assert verify_password(password, hashed) is False


class TestJWTToken:
    """Test JWT token creation and validation"""
    
    def test_create_access_token_valid(self):
        """Test pembuatan token yang valid"""
        data = {"sub": "USR001", "email": "user@example.com", "role": "CLIENT"}
        token = create_access_token(data)
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)
    
    def test_create_access_token_with_expiration(self):
        """Test pembuatan token dengan expiration custom"""
        data = {"sub": "USR001"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)
        assert token is not None
        
        # Decode and check expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload
    
    def test_create_access_token_contains_data(self):
        """Test bahwa token mengandung data yang diberikan"""
        data = {"sub": "USR001", "email": "user@example.com", "role": "CLIENT"}
        token = create_access_token(data)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert payload["sub"] == "USR001"
        assert payload["email"] == "user@example.com"
        assert payload["role"] == "CLIENT"
    
    def test_decode_access_token_valid(self):
        """Test decode token yang valid"""
        data = {"sub": "USR001", "email": "user@example.com"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        
        assert payload is not None
        assert payload["sub"] == "USR001"
        assert payload["email"] == "user@example.com"
    
    def test_decode_access_token_invalid(self):
        """Test decode token yang invalid"""
        invalid_token = "invalid.token.here"
        payload = decode_access_token(invalid_token)
        assert payload is None
    
    def test_decode_access_token_expired(self):
        """Test decode token yang expired"""
        data = {"sub": "USR001"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta)
        payload = decode_access_token(token)
        assert payload is None
    
    def test_decode_access_token_empty_string(self):
        """Test decode token string kosong"""
        payload = decode_access_token("")
        assert payload is None
    
    def test_decode_access_token_malformed(self):
        """Test decode token malformed"""
        malformed_tokens = [
            "not.a.token",
            "invalid",
            "a.b",
            "..."
        ]
        for token in malformed_tokens:
            payload = decode_access_token(token)
            assert payload is None
    
    def test_token_contains_expiration(self):
        """Test bahwa token selalu mengandung expiration"""
        data = {"sub": "USR001"}
        token = create_access_token(data)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
    
    def test_create_token_with_empty_data(self):
        """Test pembuatan token dengan data kosong"""
        data = {}
        token = create_access_token(data)
        assert token is not None
        
        payload = decode_access_token(token)
        assert payload is not None
        assert "exp" in payload


class TestPasswordEdgeCases:
    """Test edge cases untuk password"""
    
    def test_special_characters_password(self):
        """Test password dengan special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_unicode_password(self):
        """Test password dengan unicode characters"""
        password = "password密码🔒"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_minimum_length_password(self):
        """Test password dengan panjang minimum"""
        password = "a"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_exactly_72_bytes_password(self):
        """Test password dengan exactly 72 bytes"""
        password = "a" * 72
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_whitespace_password(self):
        """Test password dengan whitespace"""
        password = "pass word 123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
