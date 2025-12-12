"""
Tests untuk delete methods di repository.py
Meningkatkan coverage repository dari 82%
"""
import pytest
from app.infrastructure.repository import (
    InMemoryBookingRepository
)
from app.domain.entities import BookingSession, BookingStatus
from app.domain.value_objects import TimeSlot, SessionDuration
from datetime import date, time


class TestBookingRepositoryDeleteMethod:
    """Test delete method di BookingRepository"""
    
    def test_delete_existing_booking(self):
        """Test delete booking yang ada"""
        repo = InMemoryBookingRepository()
        
        # Create and save booking
        time_slot = TimeSlot(
            date=date(2024, 1, 15),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        duration = SessionDuration(minutes=60)
        
        booking = BookingSession(
            booking_id="BK001",
            client_id="CL001",
            trainer_id="TR001",
            time_slot=time_slot,
            duration=duration,
            status=BookingStatus.PENDING
        )
        repo.save(booking)
        
        # Delete booking
        result = repo.delete("BK001")
        assert result is True
        assert repo.find_by_id("BK001") is None
    
    def test_delete_nonexistent_booking(self):
        """Test delete booking yang tidak ada"""
        repo = InMemoryBookingRepository()
        result = repo.delete("NONEXISTENT")
        assert result is False

