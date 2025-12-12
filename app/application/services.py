"""
Application Service: BookingService
Mengatur pembuatan dan validasi booking
Sesuai dengan arsitektur DDD
"""

import uuid
from datetime import datetime
from typing import List, Optional

from app.domain.entities import BookingSession, BookingStatus, Client, Trainer
from app.domain.value_objects import SessionDuration, TimeSlot
from app.infrastructure.repository import (IBookingSessionRepository,
                                           IClientRepository, ISchedulingApi,
                                           ITrainerRepository)


class BookingService:
    """
    Application Service yang mengelola pembuatan, validasi, dan pengaturan sesi booking
    antara client dan trainer
    """

    def __init__(
        self,
        booking_repository: IBookingSessionRepository,
        client_repository: IClientRepository,
        trainer_repository: ITrainerRepository,
        scheduling_api: ISchedulingApi,
    ):
        self.booking_repository = booking_repository
        self.client_repository = client_repository
        self.trainer_repository = trainer_repository
        self.scheduling_api = scheduling_api

    def create_booking(
        self,
        client_id: str,
        trainer_id: str,
        time_slot: TimeSlot,
        duration: SessionDuration,
    ) -> BookingSession:
        """
        Membuat booking baru dengan validasi
        1. Validasi client dan trainer exists
        2. Validasi ketersediaan waktu via Scheduling API
        3. Validasi tidak ada double booking
        """
        # Validasi client exists
        client = self.client_repository.find_by_id(client_id)
        if not client:
            raise ValueError(f"Client dengan ID {client_id} tidak ditemukan")

        # Validasi trainer exists
        trainer = self.trainer_repository.find_by_id(trainer_id)
        if not trainer:
            raise ValueError(f"Trainer dengan ID {trainer_id} tidak ditemukan")

        # Validasi ketersediaan waktu via Scheduling API
        if not self.scheduling_api.check_availability(trainer_id, time_slot):
            raise ValueError("Trainer tidak tersedia pada slot waktu tersebut")

        # Validasi double booking - cek apakah ada booking lain di waktu yang sama
        existing_bookings = self.booking_repository.find_by_trainer_id(trainer_id)
        for booking in existing_bookings:
            if booking.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
                if booking.time_slot.overlaps_with(time_slot):
                    raise ValueError("Slot waktu bertabrakan dengan booking lain")

        # Buat booking baru
        booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
        booking = BookingSession(
            booking_id=booking_id,
            client_id=client_id,
            trainer_id=trainer_id,
            time_slot=time_slot,
            duration=duration,
            status=BookingStatus.PENDING,
            booking_date=datetime.now(),
        )

        # Simpan ke repository
        saved_booking = self.booking_repository.save(booking)
        return saved_booking

    def confirm_booking(self, booking_id: str, trainer_id: str) -> BookingSession:
        """
        Konfirmasi booking oleh trainer
        """
        booking = self.booking_repository.find_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking dengan ID {booking_id} tidak ditemukan")

        booking.confirm(trainer_id)
        return self.booking_repository.save(booking)

    def reject_booking(
        self, booking_id: str, trainer_id: str, reason: str
    ) -> BookingSession:
        """
        Tolak booking oleh trainer
        """
        booking = self.booking_repository.find_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking dengan ID {booking_id} tidak ditemukan")

        booking.reject(trainer_id, reason)
        return self.booking_repository.save(booking)

    def cancel_booking(
        self, booking_id: str, user_id: str, reason: str
    ) -> BookingSession:
        """
        Batalkan booking oleh client atau trainer
        """
        booking = self.booking_repository.find_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking dengan ID {booking_id} tidak ditemukan")

        booking.cancel(user_id, reason)
        return self.booking_repository.save(booking)

    def complete_booking(self, booking_id: str) -> BookingSession:
        """
        Tandai booking sebagai selesai
        """
        booking = self.booking_repository.find_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking dengan ID {booking_id} tidak ditemukan")

        booking.complete()
        return self.booking_repository.save(booking)

    def get_booking(self, booking_id: str) -> Optional[BookingSession]:
        """
        Ambil detail booking berdasarkan ID
        """
        return self.booking_repository.find_by_id(booking_id)

    def get_all_bookings(self) -> List[BookingSession]:
        """
        Ambil semua booking
        """
        return self.booking_repository.find_all()

    def get_bookings_by_client(self, client_id: str) -> List[BookingSession]:
        """
        Ambil semua booking milik client tertentu
        """
        return self.booking_repository.find_by_client_id(client_id)

    def get_bookings_by_trainer(self, trainer_id: str) -> List[BookingSession]:
        """
        Ambil semua booking untuk trainer tertentu
        """
        return self.booking_repository.find_by_trainer_id(trainer_id)


class ClientService:
    """Service untuk mengelola Client"""

    def __init__(self, client_repository: IClientRepository):
        self.client_repository = client_repository

    def create_client(
        self, name: str, email: str, phone: str, fitness_goals: Optional[str] = None
    ) -> Client:
        """Membuat client baru"""
        client_id = f"CL{uuid.uuid4().hex[:8].upper()}"
        user_id = f"USR{uuid.uuid4().hex[:8].upper()}"

        client = Client(
            client_id=client_id,
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            fitness_goals=fitness_goals,
        )
        return self.client_repository.save(client)

    def get_client(self, client_id: str) -> Optional[Client]:
        """Ambil client berdasarkan ID"""
        return self.client_repository.find_by_id(client_id)

    def get_all_clients(self) -> List[Client]:
        """Ambil semua client"""
        return self.client_repository.find_all()


class TrainerService:
    """Service untuk mengelola Trainer"""

    def __init__(self, trainer_repository: ITrainerRepository):
        self.trainer_repository = trainer_repository

    def create_trainer(
        self,
        name: str,
        email: str,
        phone: str,
        specialty: Optional[str] = None,
        certification: Optional[str] = None,
        experience: Optional[int] = None,
    ) -> Trainer:
        """Membuat trainer baru"""
        trainer_id = f"TR{uuid.uuid4().hex[:8].upper()}"
        user_id = f"USR{uuid.uuid4().hex[:8].upper()}"

        trainer = Trainer(
            trainer_id=trainer_id,
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            specialty=specialty,
            certification=certification,
            experience=experience,
        )
        return self.trainer_repository.save(trainer)

    def get_trainer(self, trainer_id: str) -> Optional[Trainer]:
        """Ambil trainer berdasarkan ID"""
        return self.trainer_repository.find_by_id(trainer_id)

    def get_all_trainers(self) -> List[Trainer]:
        """Ambil semua trainer"""
        return self.trainer_repository.find_all()
