"""
Entities untuk Booking Context
Sesuai dengan desain DDD dari dokumen
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from .value_objects import SessionDuration, TimeSlot


class BookingStatus(str, Enum):
    """
    Enumeration: Menandakan status sesi booking
    PENDING: Menunggu konfirmasi trainer
    CONFIRMED: Dikonfirmasi oleh trainer
    CANCELLED: Dibatalkan
    COMPLETED: Sesi selesai
    """

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class UserRole(str, Enum):
    """
    Enumeration: Role pengguna dalam sistem
    CLIENT: Pengguna yang melakukan booking
    TRAINER: Pelatih yang menyediakan layanan
    ADMIN: Administrator sistem
    """

    CLIENT = "CLIENT"
    TRAINER = "TRAINER"
    ADMIN = "ADMIN"


class User(BaseModel):
    """
    Entity: Pengguna sistem dengan autentikasi
    Atribut: user_id, email, hashed_password, role, is_active, created_at
    """

    user_id: str
    email: EmailStr
    hashed_password: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "USR001",
                "email": "user@example.com",
                "hashed_password": "$2b$12$...",
                "role": "CLIENT",
                "is_active": True,
                "created_at": "2025-12-01T10:00:00",
            }
        }


class Client(BaseModel):
    """
    Entity: Menyimpan data pengguna yang melakukan pemesanan sesi latihan
    Atribut: clientId, userId, name, email, phone, fitnessGoals
    """

    client_id: str
    user_id: str
    name: str
    email: str
    phone: str
    fitness_goals: Optional[str] = None

    def get_profile(self) -> dict:
        """Menampilkan informasi profil dan tujuan kebugaran klien"""
        return {
            "client_id": self.client_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "fitness_goals": self.fitness_goals,
        }

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "CL001",
                "user_id": "USR001",
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+6281234567890",
                "fitness_goals": "Weight loss and muscle building",
            }
        }


class Trainer(BaseModel):
    """
    Entity: Menyimpan data pelatih yang menyediakan layanan kebugaran
    Atribut: trainerId, userId, name, email, phone, specialty, certification, experience
    """

    trainer_id: str
    user_id: str
    name: str
    email: str
    phone: str
    specialty: Optional[str] = None
    certification: Optional[str] = None
    experience: Optional[int] = Field(None, description="Pengalaman dalam tahun")

    def get_profile(self) -> dict:
        """Menampilkan profil dan bidang keahlian pelatih"""
        return {
            "trainer_id": self.trainer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "specialty": self.specialty,
            "certification": self.certification,
            "experience": self.experience,
        }

    class Config:
        json_schema_extra = {
            "example": {
                "trainer_id": "TR001",
                "user_id": "USR002",
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+6281234567891",
                "specialty": "Strength training, Weight loss",
                "certification": "NASM-CPT, ACE",
                "experience": 5,
            }
        }


class BookingSession(BaseModel):
    """
    Aggregate Root: Entitas utama yang mengatur keseluruhan siklus hidup sesi latihan
    Mengelola hubungan antara Client, Trainer, TimeSlot dan SessionDuration

    Atribut: bookingId, clientId, trainerId, timeSlot, status, duration,
             bookingDate, confirmedDate, cancellationReason
    """

    booking_id: str
    client_id: str
    trainer_id: str
    time_slot: TimeSlot
    status: BookingStatus = BookingStatus.PENDING
    duration: SessionDuration
    booking_date: datetime = Field(default_factory=datetime.now)
    confirmed_date: Optional[datetime] = None
    cancellation_reason: Optional[str] = None

    def confirm(self, trainer_id: str) -> bool:
        """
        Mengonfirmasi sesi latihan oleh trainer
        """
        if self.trainer_id != trainer_id:
            raise ValueError("Hanya trainer yang bersangkutan yang dapat konfirmasi")

        if self.status != BookingStatus.PENDING:
            raise ValueError(
                f"Booking dengan status {self.status} tidak dapat dikonfirmasi"
            )

        self.status = BookingStatus.CONFIRMED
        self.confirmed_date = datetime.now()
        return True

    def reject(self, trainer_id: str, reason: str) -> bool:
        """
        Menolak permintaan booking dengan alasan tertentu
        """
        if self.trainer_id != trainer_id:
            raise ValueError("Hanya trainer yang bersangkutan yang dapat menolak")

        if self.status != BookingStatus.PENDING:
            raise ValueError(f"Booking dengan status {self.status} tidak dapat ditolak")

        self.status = BookingStatus.CANCELLED
        self.cancellation_reason = f"Ditolak oleh trainer: {reason}"
        return True

    def cancel(self, user_id: str, reason: str) -> bool:
        """
        Membatalkan sesi latihan
        Dapat dilakukan oleh client atau trainer
        """
        if self.status == BookingStatus.COMPLETED:
            raise ValueError("Booking yang sudah selesai tidak dapat dibatalkan")

        if self.status == BookingStatus.CANCELLED:
            raise ValueError("Booking sudah dibatalkan sebelumnya")

        self.status = BookingStatus.CANCELLED
        self.cancellation_reason = reason
        return True

    def complete(self) -> bool:
        """
        Menandai sesi latihan telah selesai dilakukan
        """
        if self.status != BookingStatus.CONFIRMED:
            raise ValueError("Hanya booking yang confirmed dapat diselesaikan")

        self.status = BookingStatus.COMPLETED
        return True

    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": "BK001",
                "client_id": "CL001",
                "trainer_id": "TR001",
                "time_slot": {
                    "date": "2025-11-20",
                    "start_time": "09:00:00",
                    "end_time": "10:00:00",
                },
                "status": "PENDING",
                "duration": {"minutes": 60},
                "booking_date": "2025-11-16T10:30:00",
                "confirmed_date": None,
                "cancellation_reason": None,
            }
        }
