"""
Unit tests untuk Value Objects
Test coverage: TimeSlot dan SessionDuration dengan edge cases
"""
import pytest
from datetime import date, time
from app.domain.value_objects import TimeSlot, SessionDuration
from pydantic import ValidationError


class TestTimeSlot:
    """Test TimeSlot Value Object"""
    
    def test_valid_time_slot(self):
        """Test pembuatan time slot yang valid"""
        ts = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        assert ts.date == date(2025, 12, 5)
        assert ts.start_time == time(9, 0)
        assert ts.end_time == time(10, 0)
    
    def test_end_time_before_start_time_raises_error(self):
        """Test end_time sebelum start_time harus error"""
        with pytest.raises(ValidationError) as exc_info:
            TimeSlot(
                date=date(2025, 12, 5),
                start_time=time(10, 0),
                end_time=time(9, 0)
            )
        assert "end_time harus setelah start_time" in str(exc_info.value)
    
    def test_end_time_equals_start_time_raises_error(self):
        """Test end_time sama dengan start_time harus error"""
        with pytest.raises(ValidationError) as exc_info:
            TimeSlot(
                date=date(2025, 12, 5),
                start_time=time(9, 0),
                end_time=time(9, 0)
            )
        assert "end_time harus setelah start_time" in str(exc_info.value)
    
    def test_overlaps_with_same_time_slot(self):
        """Test overlap dengan time slot yang sama persis"""
        ts1 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        ts2 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        assert ts1.overlaps_with(ts2) is True
    
    def test_overlaps_with_partial_overlap_start(self):
        """Test overlap ketika slot kedua mulai di tengah slot pertama"""
        ts1 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        ts2 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(9, 30),
            end_time=time(10, 30)
        )
        assert ts1.overlaps_with(ts2) is True
        assert ts2.overlaps_with(ts1) is True
    
    def test_overlaps_with_partial_overlap_end(self):
        """Test overlap ketika slot kedua berakhir di tengah slot pertama"""
        ts1 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        ts2 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(8, 30),
            end_time=time(9, 30)
        )
        assert ts1.overlaps_with(ts2) is True
        assert ts2.overlaps_with(ts1) is True
    
    def test_overlaps_with_contained_slot(self):
        """Test overlap ketika slot kedua completely contained di slot pertama"""
        ts1 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(9, 0),
            end_time=time(11, 0)
        )
        ts2 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(9, 30),
            end_time=time(10, 30)
        )
        assert ts1.overlaps_with(ts2) is True
        assert ts2.overlaps_with(ts1) is True
    
    def test_no_overlap_consecutive_slots(self):
        """Test tidak overlap untuk slot yang berurutan"""
        ts1 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        ts2 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        assert ts1.overlaps_with(ts2) is False
        assert ts2.overlaps_with(ts1) is False
    
    def test_no_overlap_different_dates(self):
        """Test tidak overlap untuk tanggal berbeda"""
        ts1 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        ts2 = TimeSlot(
            date=date(2025, 12, 6),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        assert ts1.overlaps_with(ts2) is False
    
    def test_no_overlap_gap_between_slots(self):
        """Test tidak overlap ketika ada gap antara slots"""
        ts1 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        ts2 = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(11, 0),
            end_time=time(12, 0)
        )
        assert ts1.overlaps_with(ts2) is False
        assert ts2.overlaps_with(ts1) is False
    
    def test_validate_valid_slot(self):
        """Test validate() untuk slot yang valid"""
        ts = TimeSlot(
            date=date(2025, 12, 5),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        assert ts.validate() is True


class TestSessionDuration:
    """Test SessionDuration Value Object"""
    
    def test_valid_duration_minimum(self):
        """Test durasi minimum yang valid (30 menit)"""
        duration = SessionDuration(minutes=30)
        assert duration.minutes == 30
    
    def test_valid_duration_maximum(self):
        """Test durasi maximum yang valid (120 menit)"""
        duration = SessionDuration(minutes=120)
        assert duration.minutes == 120
    
    def test_valid_duration_middle(self):
        """Test durasi di tengah range (60 menit)"""
        duration = SessionDuration(minutes=60)
        assert duration.minutes == 60
    
    def test_invalid_duration_below_minimum(self):
        """Test durasi di bawah minimum harus error"""
        with pytest.raises(ValidationError) as exc_info:
            SessionDuration(minutes=29)
        assert "greater than or equal to 30" in str(exc_info.value)
    
    def test_invalid_duration_above_maximum(self):
        """Test durasi di atas maximum harus error"""
        with pytest.raises(ValidationError) as exc_info:
            SessionDuration(minutes=121)
        assert "less than or equal to 120" in str(exc_info.value)
    
    def test_invalid_duration_zero(self):
        """Test durasi 0 harus error"""
        with pytest.raises(ValidationError) as exc_info:
            SessionDuration(minutes=0)
        assert "greater than or equal to 30" in str(exc_info.value)
    
    def test_invalid_duration_negative(self):
        """Test durasi negatif harus error"""
        with pytest.raises(ValidationError) as exc_info:
            SessionDuration(minutes=-10)
        assert "greater than or equal to 30" in str(exc_info.value)
    
    def test_validate_valid_duration(self):
        """Test validate() untuk durasi yang valid"""
        duration = SessionDuration(minutes=60)
        assert duration.validate() is True
    
    def test_validate_invalid_duration_below_min(self):
        """Test validate() raises error untuk durasi invalid"""
        # Note: Validation happens at initialization, 
        # so we can't create an invalid object to call validate()
        # This test ensures pydantic validation works
        with pytest.raises(ValidationError):
            SessionDuration(minutes=20)
    
    def test_common_duration_values(self):
        """Test nilai durasi yang umum digunakan"""
        common_durations = [30, 45, 60, 90, 120]
        for mins in common_durations:
            duration = SessionDuration(minutes=mins)
            assert duration.minutes == mins
            assert duration.validate() is True
