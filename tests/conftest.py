"""
Test configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.repository import (
    InMemoryUserRepository,
    InMemoryClientRepository,
    InMemoryTrainerRepository,
    InMemoryBookingRepository,
    MockSchedulingApi
)


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def user_repository():
    """Clean user repository for each test"""
    return InMemoryUserRepository()


@pytest.fixture
def client_repository():
    """Clean client repository for each test"""
    return InMemoryClientRepository()


@pytest.fixture
def trainer_repository():
    """Clean trainer repository for each test"""
    return InMemoryTrainerRepository()


@pytest.fixture
def booking_repository():
    """Clean booking repository for each test"""
    return InMemoryBookingRepository()


@pytest.fixture
def scheduling_api():
    """Mock scheduling API for each test"""
    return MockSchedulingApi()


# Aliases for test compatibility
@pytest.fixture
def client_repo():
    """Alias for client_repository"""
    return InMemoryClientRepository()


@pytest.fixture
def trainer_repo():
    """Alias for trainer_repository"""
    return InMemoryTrainerRepository()


# Service fixtures
@pytest.fixture
def booking_service(booking_repository, client_repository, trainer_repository):
    """Create booking service fixture"""
    from app.application.services import BookingService
    return BookingService(booking_repository, client_repository, trainer_repository)


@pytest.fixture
def client_service(client_repository):
    """Create client service fixture"""
    from app.application.services import ClientService
    return ClientService(client_repository)


@pytest.fixture
def trainer_service(trainer_repository):
    """Create trainer service fixture"""
    from app.application.services import TrainerService
    return TrainerService(trainer_repository)
