"""
Comprehensive tests for auth dependencies
Testing get_current_user, role checks, and access control
"""
import pytest
from fastapi import HTTPException
from app.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_client,
    get_current_trainer,
    get_current_admin
)
from app.auth.jwt_handler import create_access_token
from app.domain.entities import User, UserRole
from app.infrastructure.repository import InMemoryUserRepository


@pytest.fixture
def user_repo():
    """Create user repository with test users"""
    repo = InMemoryUserRepository()
    
    # Active client
    client = User(
        user_id="USR001",
        email="client@test.com",
        hashed_password="hashed",
        role=UserRole.CLIENT,
        is_active=True
    )
    repo.save(client)
    
    # Active trainer
    trainer = User(
        user_id="USR002",
        email="trainer@test.com",
        hashed_password="hashed",
        role=UserRole.TRAINER,
        is_active=True
    )
    repo.save(trainer)
    
    # Active admin
    admin = User(
        user_id="USR003",
        email="admin@test.com",
        hashed_password="hashed",
        role=UserRole.ADMIN,
        is_active=True
    )
    repo.save(admin)
    
    # Inactive user
    inactive = User(
        user_id="USR004",
        email="inactive@test.com",
        hashed_password="hashed",
        role=UserRole.CLIENT,
        is_active=False
    )
    repo.save(inactive)
    
    return repo


class TestGetCurrentUser:
    """Test get_current_user dependency"""
    
    @pytest.mark.asyncio
    async def test_valid_token(self, user_repo):
        """Test with valid token"""
        token = create_access_token(
            data={"sub": "USR001", "email": "client@test.com", "role": "CLIENT"}
        )
        
        user = await get_current_user(token=token, user_repo=user_repo)
        
        assert user.user_id == "USR001"
        assert user.email == "client@test.com"
        assert user.role == UserRole.CLIENT
    
    @pytest.mark.asyncio
    async def test_invalid_token(self, user_repo):
        """Test with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="invalid_token", user_repo=user_repo)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_token_without_sub(self, user_repo):
        """Test with token missing 'sub' field"""
        # Create token without sub
        from app.auth.jwt_handler import SECRET_KEY, ALGORITHM
        from jose import jwt
        from datetime import datetime, timedelta
        
        payload = {
            "email": "test@test.com",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, user_repo=user_repo)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_user_not_found(self, user_repo):
        """Test with valid token but user doesn't exist"""
        token = create_access_token(
            data={"sub": "USR999", "email": "notfound@test.com", "role": "CLIENT"}
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, user_repo=user_repo)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_inactive_user(self, user_repo):
        """Test with inactive user"""
        token = create_access_token(
            data={"sub": "USR004", "email": "inactive@test.com", "role": "CLIENT"}
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, user_repo=user_repo)
        
        assert exc_info.value.status_code == 403
        assert "inactive" in exc_info.value.detail.lower()


class TestGetCurrentActiveUser:
    """Test get_current_active_user dependency"""
    
    @pytest.mark.asyncio
    async def test_active_user(self, user_repo):
        """Test with active user"""
        active_user = User(
            user_id="USR005",
            email="active@test.com",
            hashed_password="hashed",
            role=UserRole.CLIENT,
            is_active=True
        )
        
        result = await get_current_active_user(current_user=active_user)
        assert result.user_id == "USR005"
        assert result.is_active is True
    
    @pytest.mark.asyncio
    async def test_inactive_user_rejected(self, user_repo):
        """Test that inactive user is rejected"""
        inactive_user = User(
            user_id="USR006",
            email="inactive2@test.com",
            hashed_password="hashed",
            role=UserRole.CLIENT,
            is_active=False
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(current_user=inactive_user)
        
        assert exc_info.value.status_code == 403
        assert "Inactive user" in exc_info.value.detail


class TestGetCurrentClient:
    """Test get_current_client dependency"""
    
    @pytest.mark.asyncio
    async def test_client_access_allowed(self, user_repo):
        """Test that CLIENT role is allowed"""
        client = User(
            user_id="USR001",
            email="client@test.com",
            hashed_password="hashed",
            role=UserRole.CLIENT,
            is_active=True
        )
        
        result = await get_current_client(current_user=client)
        assert result.role == UserRole.CLIENT
    
    @pytest.mark.asyncio
    async def test_trainer_access_denied(self, user_repo):
        """Test that TRAINER role is denied"""
        trainer = User(
            user_id="USR002",
            email="trainer@test.com",
            hashed_password="hashed",
            role=UserRole.TRAINER,
            is_active=True
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_client(current_user=trainer)
        
        assert exc_info.value.status_code == 403
        assert "clients only" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_admin_access_denied(self, user_repo):
        """Test that ADMIN role is denied"""
        admin = User(
            user_id="USR003",
            email="admin@test.com",
            hashed_password="hashed",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_client(current_user=admin)
        
        assert exc_info.value.status_code == 403


class TestGetCurrentTrainer:
    """Test get_current_trainer dependency"""
    
    @pytest.mark.asyncio
    async def test_trainer_access_allowed(self, user_repo):
        """Test that TRAINER role is allowed"""
        trainer = User(
            user_id="USR002",
            email="trainer@test.com",
            hashed_password="hashed",
            role=UserRole.TRAINER,
            is_active=True
        )
        
        result = await get_current_trainer(current_user=trainer)
        assert result.role == UserRole.TRAINER
    
    @pytest.mark.asyncio
    async def test_client_access_denied(self, user_repo):
        """Test that CLIENT role is denied"""
        client = User(
            user_id="USR001",
            email="client@test.com",
            hashed_password="hashed",
            role=UserRole.CLIENT,
            is_active=True
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_trainer(current_user=client)
        
        assert exc_info.value.status_code == 403
        assert "trainers only" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_admin_access_denied(self, user_repo):
        """Test that ADMIN role is denied"""
        admin = User(
            user_id="USR003",
            email="admin@test.com",
            hashed_password="hashed",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_trainer(current_user=admin)
        
        assert exc_info.value.status_code == 403


class TestGetCurrentAdmin:
    """Test get_current_admin dependency"""
    
    @pytest.mark.asyncio
    async def test_admin_access_allowed(self, user_repo):
        """Test that ADMIN role is allowed"""
        admin = User(
            user_id="USR003",
            email="admin@test.com",
            hashed_password="hashed",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        result = await get_current_admin(current_user=admin)
        assert result.role == UserRole.ADMIN
    
    @pytest.mark.asyncio
    async def test_client_access_denied(self, user_repo):
        """Test that CLIENT role is denied"""
        client = User(
            user_id="USR001",
            email="client@test.com",
            hashed_password="hashed",
            role=UserRole.CLIENT,
            is_active=True
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin(current_user=client)
        
        assert exc_info.value.status_code == 403
        assert "admins only" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_trainer_access_denied(self, user_repo):
        """Test that TRAINER role is denied"""
        trainer = User(
            user_id="USR002",
            email="trainer@test.com",
            hashed_password="hashed",
            role=UserRole.TRAINER,
            is_active=True
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin(current_user=trainer)
        
        assert exc_info.value.status_code == 403


class TestRequireRoleFactory:
    """Test require_role factory function"""
    
    @pytest.mark.asyncio
    async def test_require_role_client_allowed(self, user_repo):
        """Test require_role factory allows correct role"""
        from app.auth.dependencies import require_role
        
        client = User(
            user_id="USR001",
            email="client@test.com",
            hashed_password="hashed",
            role=UserRole.CLIENT,
            is_active=True
        )
        
        role_checker = await require_role(UserRole.CLIENT)
        result = await role_checker(current_user=client)
        
        assert result.role == UserRole.CLIENT
    
    @pytest.mark.asyncio
    async def test_require_role_denied(self, user_repo):
        """Test require_role factory denies incorrect role"""
        from app.auth.dependencies import require_role
        
        client = User(
            user_id="USR001",
            email="client@test.com",
            hashed_password="hashed",
            role=UserRole.CLIENT,
            is_active=True
        )
        
        role_checker = await require_role(UserRole.ADMIN)
        
        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user=client)
        
        assert exc_info.value.status_code == 403
        assert "Required role: ADMIN" in exc_info.value.detail
