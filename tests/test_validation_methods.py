"""
Test untuk mencapai 95%+ coverage - target missing lines spesifik
"""
import pytest
from datetime import date, time
from app.domain.value_objects import TimeSlot, SessionDuration


class TestValueObjectsValidation:
    """Test untuk method validate() yang belum tercovered"""
    
    def test_timeslot_validate_success(self):
        """Test validate method dengan TimeSlot yang valid - lines 43, 45"""
        slot = TimeSlot(
            date=date(2024, 1, 15),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        # Panggil validate() explicitly
        assert slot.validate() == True
    
    def test_timeslot_validate_with_valid_data(self):
        """Test validate tidak raise error untuk data valid"""
        slot = TimeSlot(
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 30)
        )
        # Method validate dipanggil dan return True
        result = slot.validate()
        assert result is True


class TestSessionDurationValidation:
    """Test untuk SessionDuration validate method"""
    
    def test_session_duration_validate_success(self):
        """Test validate method untuk durasi valid - line 71"""
        duration = SessionDuration(minutes=60)
        # Panggil validate explicitly
        assert duration.validate() == True
    
    def test_session_duration_validate_minimum(self):
        """Test validate untuk durasi minimum"""
        duration = SessionDuration(minutes=30)
        result = duration.validate()
        assert result is True
    
    def test_session_duration_validate_maximum(self):
        """Test validate untuk durasi maximum"""
        duration = SessionDuration(minutes=120)
        result = duration.validate()
        assert result is True
