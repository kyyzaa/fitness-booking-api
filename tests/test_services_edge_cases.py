"""
Comprehensive tests for application services
Focus on edge cases and error handling to reach 95%+ coverage
"""
import pytest
from datetime import date, time
from app.application.services import BookingService, ClientService, TrainerService
from app.infrastructure.repository import (
    InMemoryBookingRepository,
    InMemoryClientRepository,
    InMemoryTrainerRepository,
    MockSchedulingApi
)
from app.domain.entities import Client, Trainer, BookingSession, BookingStatus
from app.domain.value_objects import TimeSlot, SessionDuration


class TestBookingServiceEdgeCases:
    """Test edge cases and error paths for BookingService"""
    
    def test_create_booking_nonexistent_client(self):
        """Test create booking dengan client yang tidak ada"""
        booking_repo = InMemoryBookingRepository()
        client_repo = InMemoryClientRepository()
        trainer_repo = InMemoryTrainerRepository()
        scheduling_api = MockSchedulingApi()
        
        # Save trainer but not client
        trainer = Trainer(
            trainer_id="TR001",
            user_id="USR001",
            name="Trainer One",
            email="trainer@example.com",
            phone="081234567890",
            specialty="Yoga"
        )
        trainer_repo.save(trainer)
        
        service = BookingService(booking_repo, client_repo, trainer_repo, scheduling_api)
        
        time_slot = TimeSlot(
            date=date(2024, 1, 15),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        duration = SessionDuration(minutes=60)
        
        with pytest.raises(ValueError, match="Client dengan ID .* tidak ditemukan"):
            service.create_booking("NONEXISTENT_CLIENT", "TR001", time_slot, duration)
    
    def test_create_booking_nonexistent_trainer(self):
        """Test create booking dengan trainer yang tidak ada"""
        booking_repo = InMemoryBookingRepository()
        client_repo = InMemoryClientRepository()
        trainer_repo = InMemoryTrainerRepository()
        scheduling_api = MockSchedulingApi()
        
        # Save client but not trainer
        client = Client(
            client_id="CL001",
            user_id="USR001",
            name="Client One",
            email="client@example.com",
            phone="081234567890",
            fitness_goals="Weight loss"
        )
        client_repo.save(client)
        
        service = BookingService(booking_repo, client_repo, trainer_repo, scheduling_api)
        
        time_slot = TimeSlot(
            date=date(2024, 1, 15),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        duration = SessionDuration(minutes=60)
        
        with pytest.raises(ValueError, match="Trainer dengan ID .* tidak ditemukan"):
            service.create_booking("CL001", "NONEXISTENT_TRAINER", time_slot, duration)
    
    def test_create_booking_overlapping_time(self):
        """Test create booking dengan waktu yang bertabrakan"""
        booking_repo = InMemoryBookingRepository()
        client_repo = InMemoryClientRepository()
        trainer_repo = InMemoryTrainerRepository()
        scheduling_api = MockSchedulingApi()
        
        # Save client and trainer
        client = Client(
            client_id="CL001",
            user_id="USR001",
            name="Client One",
            email="client@example.com",
            phone="081234567890",
            fitness_goals="Weight loss"
        )
        trainer = Trainer(
            trainer_id="TR001",
            user_id="USR002",
            name="Trainer One",
            email="trainer@example.com",
            phone="081234567890",
            specialty="Yoga"
        )
        client_repo.save(client)
        trainer_repo.save(trainer)
        
        service = BookingService(booking_repo, client_repo, trainer_repo, scheduling_api)
        service = BookingService(booking_repo, client_repo, trainer_repo, scheduling_api)
        
        time_slot = TimeSlot(
            date=date(2024, 1, 15),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        duration = SessionDuration(minutes=60)
        
        # Create first booking
        service.create_booking("CL001", "TR001", time_slot, duration)
        
        # Try to create overlapping booking
        overlapping_slot = TimeSlot(
            date=date(2024, 1, 15),
            start_time=time(10, 30),
            end_time=time(11, 30)
        )
        with pytest.raises(ValueError, match="bertabrakan dengan booking lain"):
            service.create_booking("CL001", "TR001", overlapping_slot, duration)
    
    def test_confirm_nonexistent_booking(self):
        """Test confirm booking yang tidak ada"""
        booking_repo = InMemoryBookingRepository()
        client_repo = InMemoryClientRepository()
        trainer_repo = InMemoryTrainerRepository()
        scheduling_api = MockSchedulingApi()
        
        service = BookingService(booking_repo, client_repo, trainer_repo, scheduling_api)
        
        with pytest.raises(ValueError, match="tidak ditemukan"):
            service.confirm_booking("NONEXISTENT", "TR001")
    
    def test_reject_nonexistent_booking(self):
        """Test reject booking yang tidak ada"""
        booking_repo = InMemoryBookingRepository()
        client_repo = InMemoryClientRepository()
        trainer_repo = InMemoryTrainerRepository()
        scheduling_api = MockSchedulingApi()
        
        service = BookingService(booking_repo, client_repo, trainer_repo, scheduling_api)
        
        with pytest.raises(ValueError, match="tidak ditemukan"):
            service.reject_booking("NONEXISTENT", "TR001", "Not available")
    
    def test_cancel_nonexistent_booking(self):
        """Test cancel booking yang tidak ada"""
        booking_repo = InMemoryBookingRepository()
        client_repo = InMemoryClientRepository()
        trainer_repo = InMemoryTrainerRepository()
        scheduling_api = MockSchedulingApi()
        
        service = BookingService(booking_repo, client_repo, trainer_repo, scheduling_api)
        
        with pytest.raises(ValueError, match="tidak ditemukan"):
            service.cancel_booking("NONEXISTENT", "USR001", "Changed plans")
    
    def test_complete_nonexistent_booking(self):
        """Test complete booking yang tidak ada"""
        booking_repo = InMemoryBookingRepository()
        client_repo = InMemoryClientRepository()
        trainer_repo = InMemoryTrainerRepository()
        scheduling_api = MockSchedulingApi()
        
        service = BookingService(booking_repo, client_repo, trainer_repo, scheduling_api)
        
        with pytest.raises(ValueError, match="tidak ditemukan"):
            service.complete_booking("NONEXISTENT")
    
    # Note: MockSchedulingApi always returns True, so we can't easily test unavailable trainer
    # Would need to modify MockSchedulingApi or use a different mock
    
    def test_get_nonexistent_booking(self):
        """Test get booking yang tidak ada returns None"""
        booking_repo = InMemoryBookingRepository()
        client_repo = InMemoryClientRepository()
        trainer_repo = InMemoryTrainerRepository()
        scheduling_api = MockSchedulingApi()
        
        service = BookingService(booking_repo, client_repo, trainer_repo, scheduling_api)
        
        result = service.get_booking("NONEXISTENT")
        assert result is None


class TestClientServiceEdgeCases:
    """Test edge cases for ClientService"""
    
    def test_get_nonexistent_client(self):
        """Test get client yang tidak ada"""
        repo = InMemoryClientRepository()
        service = ClientService(repo)
        
        result = service.get_client("NONEXISTENT")
        assert result is None
    
    def test_get_all_clients_empty(self):
        """Test get all clients dari empty repository"""
        repo = InMemoryClientRepository()
        service = ClientService(repo)
        
        clients = service.get_all_clients()
        assert clients == []
    
    def test_create_multiple_clients(self):
        """Test create multiple clients"""
        repo = InMemoryClientRepository()
        service = ClientService(repo)
        
        for i in range(3):
            client = service.create_client(
                name=f"Client {i}",
                email=f"client{i}@test.com",
                phone=f"+628123456789{i}"
            )
            assert client.name == f"Client {i}"
        
        all_clients = service.get_all_clients()
        assert len(all_clients) == 3


class TestTrainerServiceEdgeCases:
    """Test edge cases for TrainerService"""
    
    def test_get_nonexistent_trainer(self):
        """Test get trainer yang tidak ada"""
        repo = InMemoryTrainerRepository()
        service = TrainerService(repo)
        
        result = service.get_trainer("NONEXISTENT")
        assert result is None
    
    def test_get_all_trainers_empty(self):
        """Test get all trainers dari empty repository"""
        repo = InMemoryTrainerRepository()
        service = TrainerService(repo)
        
        trainers = service.get_all_trainers()
        assert trainers == []
    
    def test_create_multiple_trainers(self):
        """Test create multiple trainers"""
        repo = InMemoryTrainerRepository()
        service = TrainerService(repo)
        
        for i in range(3):
            trainer = service.create_trainer(
                name=f"Trainer {i}",
                email=f"trainer{i}@test.com",
                phone=f"+628123456780{i}"
            )
            assert trainer.name == f"Trainer {i}"
        
        all_trainers = service.get_all_trainers()
        assert len(all_trainers) == 3
