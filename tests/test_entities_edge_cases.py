"""
Test edge cases untuk entities
"""
import pytest
from datetime import date, time
from app.domain.entities import Client, Trainer, BookingSession, BookingStatus
from app.domain.value_objects import TimeSlot, SessionDuration


class TestClientEdgeCases:
    """Test edge cases untuk Client entity"""
    
    def test_client_get_profile(self):
        """Test get_profile method - line 77"""
        client = Client(
            client_id="CL001",
            user_id="USR001",
            name="Test Client",
            email="client@test.com",
            phone="+6281234567890",
            fitness_goals="Weight Loss and Cardio"
        )
        
        profile = client.get_profile()
        assert profile["client_id"] == "CL001"
        assert profile["name"] == "Test Client"
        assert profile["email"] == "client@test.com"
        assert "fitness_goals" in profile


class TestTrainerEdgeCases:
    """Test edge cases untuk Trainer entity"""
    
    def test_trainer_get_profile(self):
        """Test get_profile method - line 114"""
        trainer = Trainer(
            trainer_id="TR001",
            user_id="USR002",
            name="Test Trainer",
            email="trainer@test.com",
            phone="+6281234567891",
            expertise="Cardio and Strength Training"
        )
        
        profile = trainer.get_profile()
        assert profile["trainer_id"] == "TR001"
        assert profile["name"] == "Test Trainer"
        assert profile["email"] == "trainer@test.com"
        assert "trainer_id" in profile


class TestBookingSessionEdgeCases:
    """Test edge cases untuk BookingSession"""
    
    def test_reject_booking_with_wrong_status(self):
        """Test reject booking yang sudah confirmed - line 179"""
        time_slot = TimeSlot(
            date=date(2024, 1, 15),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        booking = BookingSession(
            booking_id="BK001",
            client_id="CL001",
            trainer_id="TR001",
            time_slot=time_slot,
            duration=SessionDuration(minutes=60)
        )
        
        # Confirm dulu
        booking.confirm("TR001")
        
        # Coba reject booking yang sudah confirmed
        with pytest.raises(ValueError, match="tidak dapat ditolak"):
            booking.reject("TR001", "Tidak tersedia")
    
    def test_cancel_already_cancelled_booking(self):
        """Test cancel booking yang sudah dibatalkan - line 194"""
        time_slot = TimeSlot(
            date=date(2024, 1, 15),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        booking = BookingSession(
            booking_id="BK001",
            client_id="CL001",
            trainer_id="TR001",
            time_slot=time_slot,
            duration=SessionDuration(minutes=60)
        )
        
        # Cancel pertama kali
        booking.cancel("CL001", "Tidak jadi")
        
        # Coba cancel lagi
        with pytest.raises(ValueError, match="sudah dibatalkan"):
            booking.cancel("CL001", "Cancel lagi")
