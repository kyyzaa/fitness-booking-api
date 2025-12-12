"""
Value Objects untuk Booking Context
Sesuai dengan desain DDD dari dokumen
"""
from datetime import datetime, time, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TimeSlot(BaseModel):
    """
    Value Object: Mewakili rentang waktu tertentu dalam jadwal pelatih
    Atribut: date, startTime, endTime
    """
    date: date
    start_time: time
    end_time: time

    @field_validator('end_time')
    @classmethod
    def validate_end_after_start(cls, v, info):
        """Memastikan end_time setelah start_time"""
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError("end_time harus setelah start_time")
        return v

    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """
        Memeriksa apakah dua slot waktu saling bertabrakan
        """
        if self.date != other.date:
            return False
        
        # Check if time ranges overlap
        return (self.start_time < other.end_time and 
                self.end_time > other.start_time)

    def validate(self) -> bool:
        """
        Memastikan format waktu valid dan tidak kosong
        """
        if not self.date or not self.start_time or not self.end_time:
            raise ValueError("TimeSlot tidak boleh kosong")
        if self.end_time <= self.start_time:
            raise ValueError("end_time harus setelah start_time")
        return True

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-11-20",
                "start_time": "09:00:00",
                "end_time": "10:00:00"
            }
        }


class SessionDuration(BaseModel):
    """
    Value Object: Menentukan lama waktu sesi latihan
    Atribut: minutes
    Fungsi: validate() → memastikan nilai durasi valid dan positif (30-120 menit)
    """
    minutes: int = Field(..., ge=30, le=120, description="Durasi sesi dalam menit (30-120)")

    def validate(self) -> bool:
        """
        Memastikan nilai durasi positif dan berada dalam batas yang diperbolehkan (30–120 menit)
        """
        if self.minutes < 30 or self.minutes > 120:
            raise ValueError("Durasi sesi harus antara 30-120 menit")
        return True

    class Config:
        json_schema_extra = {
            "example": {
                "minutes": 60
            }
        }
