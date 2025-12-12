"""
Tests for auth dependencies
"""
import pytest
from fastapi import HTTPException
from jose import jwt
from app.auth.dependencies import get_current_user
from app.auth.jwt_handler import SECRET_KEY, ALGORITHM, create_access_token
from app.domain.entities import User


@pytest.mark.asyncio
async def test_get_current_user_with_valid_token(client_repo):
    """Test get current user dengan token yang valid"""
    from app.domain.entities import Client
    
    # Create client
    client = Client(
        user_id="CL001",
        name="Test Client",
        email="test@test.com",
        hashed_password="hashed",
        phone="08123456789"
    )
    client_repo.save(client)
    
    # Create token
    token = create_access_token(data={"sub": "test@test.com"})
    
    # Test
    user = await get_current_user(token, client_repo, None)
    assert user is not None
    assert user.email == "test@test.com"


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token(client_repo):
    """Test get current user dengan token yang invalid"""
    invalid_token = "invalid.token.here"
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(invalid_token, client_repo, None)
    
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_with_expired_token(client_repo):
    """Test get current user dengan token yang sudah expired"""
    from datetime import timedelta
    
    # Create expired token
    token = create_access_token(
        data={"sub": "test@test.com"}, 
        expires_delta=timedelta(minutes=-1)
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, client_repo, None)
    
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_with_missing_email(client_repo):
    """Test get current user dengan token tanpa email"""
    # Create token without email
    token_data = {"sub": None}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, client_repo, None)
    
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_with_nonexistent_user(client_repo):
    """Test get current user dengan user yang tidak ada di database"""
    # Create token for non-existent user
    token = create_access_token(data={"sub": "nonexistent@test.com"})
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, client_repo, None)
    
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_from_trainer_repo(trainer_repo):
    """Test get current user dari trainer repository"""
    from app.domain.entities import Trainer
    
    # Create trainer
    trainer = Trainer(
        user_id="TR001",
        name="Test Trainer",
        email="trainer@test.com",
        hashed_password="hashed",
        phone="08198765432",
        specialization="Yoga"
    )
    trainer_repo.save(trainer)
    
    # Create token
    token = create_access_token(data={"sub": "trainer@test.com"})
    
    # Test - should check trainer repo when not found in client repo
    user = await get_current_user(token, None, trainer_repo)
    assert user is not None
    assert user.email == "trainer@test.com"


@pytest.mark.asyncio
async def test_get_current_user_token_with_extra_data(client_repo):
    """Test get current user dengan token yang memiliki extra data"""
    from app.domain.entities import Client
    
    # Create client
    client = Client(
        user_id="CL001",
        name="Test Client",
        email="test@test.com",
        hashed_password="hashed",
        phone="08123456789"
    )
    client_repo.save(client)
    
    # Create token with extra data
    token_data = {
        "sub": "test@test.com",
        "extra": "data",
        "another": "field"
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    # Test - should still work
    user = await get_current_user(token, client_repo, None)
    assert user is not None
    assert user.email == "test@test.com"


@pytest.mark.asyncio
async def test_get_current_user_with_malformed_token(client_repo):
    """Test get current user dengan token yang malformed"""
    malformed_tokens = [
        "not.a.token",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",  # Only header
        "",  # Empty string
        "Bearer token",  # With Bearer prefix
    ]
    
    for token in malformed_tokens:
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token, client_repo, None)
        assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_with_wrong_signature(client_repo):
    """Test get current user dengan token yang signature-nya salah"""
    from app.domain.entities import Client
    
    # Create client
    client = Client(
        user_id="CL001",
        name="Test Client",
        email="test@test.com",
        hashed_password="hashed",
        phone="08123456789"
    )
    client_repo.save(client)
    
    # Create token with wrong secret
    token_data = {"sub": "test@test.com"}
    wrong_token = jwt.encode(token_data, "wrong_secret_key", algorithm=ALGORITHM)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(wrong_token, client_repo, None)
    
    assert exc_info.value.status_code == 401
