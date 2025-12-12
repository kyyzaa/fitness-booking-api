"""
Complete tests untuk services.py
Meningkatkan coverage dengan testing semua error paths
"""
import pytest
from datetime import date, time
from app.application.services import BookingService
from app.infrastructure.repository import (
    InMemoryBookingRepository,
    InMemoryClientRepository,
    InMemoryTrainerRepository,
    MockSchedulingApi
)
from app.domain.entities import Client, Trainer, BookingSession, BookingStatus
from app.domain.value_objects import TimeSlot, SessionDuration


class TestBookingServiceCompleteCoverage:
    """Test semua path di BookingService"""
    
    def test_reject_booking_not_found(self):
        """Test reject booking yang tidak ditemukan - line 107"""
        booking_repo = InMemoryBookingRepository()
        client_repo = InMemoryClientRepository()
        trainer_repo = InMemoryTrainerRepository()
        scheduling_api = MockSchedulingApi()
        
        service = BookingService(booking_repo, client_repo, trainer_repo, scheduling_api)
        
        # Coba reject booking yang tidak ada
        with pytest.raises(ValueError, match="tidak ditemukan"):
            service.reject_booking("NONEXISTENT_ID", "TR001", "Not available")
    
    def test_cancel_booking_not_found(self):
        """Test cancel booking yang tidak ditemukan - line 63"""
        booking_repo = InMemoryBookingRepository()
        client_repo = InMemoryClientRepository()
        trainer_repo = InMemoryTrainerRepository()
        scheduling_api = MockSchedulingApi()
        
        service = BookingService(booking_repo, client_repo, trainer_repo, scheduling_api)
        
        # Coba cancel booking yang tidak ada - ini akan trigger line 113
        with pytest.raises(ValueError, match="tidak ditemukan"):
            service.cancel_booking("NONEXISTENT_ID", "USR001", "Changed my mind")
    
    def test_complete_booking_not_found(self):
        """Test complete booking yang tidak ditemukan"""
        booking_repo = InMemoryBookingRepository()
        client_repo = InMemoryClientRepository()
        trainer_repo = InMemoryTrainerRepository()
        scheduling_api = MockSchedulingApi()
        
        service = BookingService(booking_repo, client_repo, trainer_repo, scheduling_api)
        
        # Coba complete booking yang tidak ada
        with pytest.raises(ValueError, match="tidak ditemukan"):
            service.complete_booking("NONEXISTENT_ID")
    
    def test_full_booking_workflow(self):
        """Test complete workflow: create -> confirm -> complete"""
        booking_repo = InMemoryBookingRepository()
        client_repo = InMemoryClientRepository()
        trainer_repo = InMemoryTrainerRepository()
        scheduling_api = MockSchedulingApi()
        
        # Setup client and trainer
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
        
        # Create booking
        time_slot = TimeSlot(
            date=date(2024, 1, 15),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        duration = SessionDuration(minutes=60)
        
        booking = service.create_booking("CL001", "TR001", time_slot, duration)
        assert booking.status == BookingStatus.PENDING
        
        # Confirm booking
        confirmed = service.confirm_booking(booking.booking_id, "TR001")
        assert confirmed.status == BookingStatus.CONFIRMED
        
        # Complete booking
        completed = service.complete_booking(booking.booking_id)
        assert completed.status == BookingStatus.COMPLETED
