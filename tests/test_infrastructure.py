"""
Tests for infrastructure repository implementations
"""
import pytest
from datetime import datetime, timedelta
from app.infrastructure.repository import (
    InMemoryUserRepository,
    InMemoryClientRepository,
    InMemoryTrainerRepository,
    InMemoryBookingRepository
)
from app.domain.entities import User, UserRole


class TestInMemoryUserRepository:
    """Tests untuk InMemoryUserRepository"""
    
    def test_save_and_find_user(self):
        """Test save dan find user"""
        repo = InMemoryUserRepository()
        user = User(
            user_id="USR001",
            email="test@test.com",
            hashed_password="hashed",
            role=UserRole.CLIENT
        )
        
        repo.save(user)
        found = repo.find_by_id("USR001")
        
        assert found is not None
        assert found.email == "test@test.com"
    
    def test_find_by_email(self):
        """Test find user by email"""
        repo = InMemoryUserRepository()
        user = User(
            user_id="USR002",
            email="email@test.com",
            hashed_password="hashed",
            role=UserRole.TRAINER
        )
        
        repo.save(user)
        found = repo.find_by_email("email@test.com")
        
        assert found is not None
        assert found.user_id == "USR002"
    
    def test_find_nonexistent_user(self):
        """Test find user yang tidak ada"""
        repo = InMemoryUserRepository()
        found = repo.find_by_id("NONEXISTENT")
        
        assert found is None
    
    def test_find_all_users(self):
        """Test find all users"""
        repo = InMemoryUserRepository()
        
        for i in range(3):
            user = User(
                user_id=f"USR{i}",
                email=f"user{i}@test.com",
                hashed_password="hashed",
                role=UserRole.CLIENT
            )
            repo.save(user)
        
        users = repo.find_all()
        assert len(users) == 3


class TestInMemoryClientRepository:
    """Tests untuk InMemoryClientRepository specific methods"""
    
    def test_save_and_find_client(self):
        """Test save and find client"""
        from app.domain.entities import Client
        repo = InMemoryClientRepository()
        
        client = Client(
            client_id="CL001",
            user_id="USR001",
            name="Test Client",
            email="client@test.com",
            phone="+6281234567890"
        )
        
        repo.save(client)
        found = repo.find_by_id("CL001")
        
        assert found is not None
        assert found.name == "Test Client"
    
    def test_find_nonexistent_client(self):
        """Test find client yang tidak ada"""
        repo = InMemoryClientRepository()
        assert repo.find_by_id("NONEXISTENT") is None
    
    def test_find_all_clients(self):
        """Test find all clients"""
        from app.domain.entities import Client
        repo = InMemoryClientRepository()
        
        for i in range(2):
            client = Client(
                client_id=f"CL00{i}",
                user_id=f"USR00{i}",
                name=f"Client {i}",
                email=f"client{i}@test.com",
                phone=f"+628123456789{i}"
            )
            repo.save(client)
        
        clients = repo.find_all()
        assert len(clients) == 2
    
    def test_update_client(self):
        """Test update existing client"""
        from app.domain.entities import Client
        repo = InMemoryClientRepository()
        
        client = Client(
            client_id="CL001",
            user_id="USR001",
            name="Original Name",
            email="original@test.com",
            phone="+6281234567890"
        )
        repo.save(client)
        
        # Update
        client.name = "Updated Name"
        repo.save(client)
        
        found = repo.find_by_id("CL001")
        assert found.name == "Updated Name"


class TestInMemoryTrainerRepository:
    """Tests untuk InMemoryTrainerRepository specific methods"""
    
    def test_save_and_find_trainer(self):
        """Test save and find trainer"""
        from app.domain.entities import Trainer
        repo = InMemoryTrainerRepository()
        
        trainer = Trainer(
            trainer_id="TR001",
            user_id="USR002",
            name="Test Trainer",
            email="trainer@test.com",
            phone="+6281234567891"
        )
        
        repo.save(trainer)
        found = repo.find_by_id("TR001")
        
        assert found is not None
        assert found.name == "Test Trainer"
    
    def test_find_nonexistent_trainer(self):
        """Test find trainer yang tidak ada"""
        repo = InMemoryTrainerRepository()
        assert repo.find_by_id("NONEXISTENT") is None
    
    def test_find_all_trainers(self):
        """Test find all trainers"""
        from app.domain.entities import Trainer
        repo = InMemoryTrainerRepository()
        
        for i in range(3):
            trainer = Trainer(
                trainer_id=f"TR00{i}",
                user_id=f"USR10{i}",
                name=f"Trainer {i}",
                email=f"trainer{i}@test.com",
                phone=f"+628123456780{i}"
            )
            repo.save(trainer)
        
        trainers = repo.find_all()
        assert len(trainers) == 3


class TestInMemoryBookingRepository:
    """Tests untuk InMemoryBookingRepository specific methods"""
    
    def test_save_and_find_booking(self):
        """Test save and find booking"""
        from app.domain.entities import BookingSession
        from app.domain.value_objects import TimeSlot, SessionDuration
        from datetime import date, time
        
        repo = InMemoryBookingRepository()
        
        time_slot = TimeSlot(
            date=date(2025, 12, 20),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        duration = SessionDuration(minutes=60)
        
        booking = BookingSession(
            booking_id="BK001",
            client_id="CL001",
            trainer_id="TR001",
            time_slot=time_slot,
            duration=duration
        )
        
        repo.save(booking)
        found = repo.find_by_id("BK001")
        
        assert found is not None
        assert found.client_id == "CL001"
    
    def test_find_by_client_with_bookings(self):
        """Test find by client dengan bookings"""
        from app.domain.entities import BookingSession
        from app.domain.value_objects import TimeSlot, SessionDuration
        from datetime import date, time
        
        repo = InMemoryBookingRepository()
        
        for i in range(2):
            time_slot = TimeSlot(
                date=date(2025, 12, 20 + i),
                start_time=time(9 + i, 0),
                end_time=time(10 + i, 0)
            )
            duration = SessionDuration(minutes=60)
            
            booking = BookingSession(
                booking_id=f"BK00{i}",
                client_id="CL001",
                trainer_id=f"TR00{i}",
                time_slot=time_slot,
                duration=duration
            )
            repo.save(booking)
        
        bookings = repo.find_by_client_id("CL001")
        assert len(bookings) == 2
    
    def test_find_by_trainer_with_bookings(self):
        """Test find by trainer dengan bookings"""
        from app.domain.entities import BookingSession
        from app.domain.value_objects import TimeSlot, SessionDuration
        from datetime import date, time
        
        repo = InMemoryBookingRepository()
        
        for i in range(3):
            time_slot = TimeSlot(
                date=date(2025, 12, 20 + i),
                start_time=time(10 + i, 0),
                end_time=time(11 + i, 0)
            )
            duration = SessionDuration(minutes=60)
            
            booking = BookingSession(
                booking_id=f"BK10{i}",
                client_id=f"CL00{i}",
                trainer_id="TR001",
                time_slot=time_slot,
                duration=duration
            )
            repo.save(booking)
        
        bookings = repo.find_by_trainer_id("TR001")
        assert len(bookings) == 3
    
    def test_find_by_client_empty(self):
        """Test find by client ketika kosong"""
        repo = InMemoryBookingRepository()
        bookings = repo.find_by_client_id("CL001")
        
        assert bookings == []
    
    def test_find_by_trainer_empty(self):
        """Test find by trainer ketika kosong"""
        repo = InMemoryBookingRepository()
        bookings = repo.find_by_trainer_id("TR001")
        
        assert bookings == []
    
    def test_find_all_empty(self):
        """Test find all ketika repository kosong"""
        repo = InMemoryBookingRepository()
        bookings = repo.find_all()
        
        assert bookings == []
    
    def test_find_all_with_bookings(self):
        """Test find all dengan bookings"""
        from app.domain.entities import BookingSession
        from app.domain.value_objects import TimeSlot, SessionDuration
        from datetime import date, time
        
        repo = InMemoryBookingRepository()
        
        for i in range(4):
            time_slot = TimeSlot(
                date=date(2025, 12, 20),
                start_time=time(8 + i, 0),
                end_time=time(9 + i, 0)
            )
            duration = SessionDuration(minutes=60)
            
            booking = BookingSession(
                booking_id=f"BK20{i}",
                client_id=f"CL00{i}",
                trainer_id=f"TR00{i}",
                time_slot=time_slot,
                duration=duration
            )
            repo.save(booking)
        
        bookings = repo.find_all()
        assert len(bookings) == 4
