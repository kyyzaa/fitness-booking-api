"""
API Routes untuk Booking Context
RESTful endpoints untuk mengelola BookingSession
"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import date, time

from app.domain.entities import BookingSession, BookingStatus, User
from app.domain.value_objects import TimeSlot, SessionDuration
from app.application.services import BookingService
from app.auth.dependencies import get_current_user, get_current_active_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# Request/Response DTOs
class TimeSlotDTO(BaseModel):
    date: date
    start_time: time
    end_time: time
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-11-20",
                "start_time": "09:00:00",
                "end_time": "10:00:00"
            }
        }


class CreateBookingRequest(BaseModel):
    client_id: str
    trainer_id: str
    time_slot: TimeSlotDTO
    duration_minutes: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "CL001",
                "trainer_id": "TR001",
                "time_slot": {
                    "date": "2025-11-20",
                    "start_time": "09:00:00",
                    "end_time": "10:00:00"
                },
                "duration_minutes": 60
            }
        }


class ConfirmBookingRequest(BaseModel):
    trainer_id: str
    
    class Config:
        json_schema_extra = {
            "example": {"trainer_id": "TR001"}
        }


class RejectBookingRequest(BaseModel):
    trainer_id: str
    reason: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "trainer_id": "TR001",
                "reason": "Jadwal bentrok dengan sesi lain"
            }
        }


class CancelBookingRequest(BaseModel):
    user_id: str
    reason: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "USR001",
                "reason": "Client berhalangan hadir"
            }
        }


class BookingResponse(BaseModel):
    booking_id: str
    client_id: str
    trainer_id: str
    time_slot: TimeSlotDTO
    status: BookingStatus
    duration_minutes: int
    booking_date: str
    confirmed_date: str | None
    cancellation_reason: str | None
    
    @classmethod
    def from_entity(cls, booking: BookingSession):
        return cls(
            booking_id=booking.booking_id,
            client_id=booking.client_id,
            trainer_id=booking.trainer_id,
            time_slot=TimeSlotDTO(
                date=booking.time_slot.date,
                start_time=booking.time_slot.start_time,
                end_time=booking.time_slot.end_time
            ),
            status=booking.status,
            duration_minutes=booking.duration.minutes,
            booking_date=booking.booking_date.isoformat(),
            confirmed_date=booking.confirmed_date.isoformat() if booking.confirmed_date else None,
            cancellation_reason=booking.cancellation_reason
        )


# Dependency injection untuk service
def get_booking_service() -> BookingService:
    from app.main import booking_service
    return booking_service


@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(
    request: CreateBookingRequest,
    service: BookingService = Depends(get_booking_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Membuat booking session baru
    
    **Memerlukan autentikasi (JWT token)**
    
    - **client_id**: ID client yang melakukan booking
    - **trainer_id**: ID trainer yang akan melatih
    - **time_slot**: Slot waktu untuk sesi latihan
    - **duration_minutes**: Durasi sesi dalam menit (30-120)
    """
    try:
        time_slot = TimeSlot(
            date=request.time_slot.date,
            start_time=request.time_slot.start_time,
            end_time=request.time_slot.end_time
        )
        duration = SessionDuration(minutes=request.duration_minutes)
        
        booking = service.create_booking(
            client_id=request.client_id,
            trainer_id=request.trainer_id,
            time_slot=time_slot,
            duration=duration
        )
        return BookingResponse.from_entity(booking)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[BookingResponse])
def get_all_bookings(
    service: BookingService = Depends(get_booking_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mengambil semua booking sessions
    
    **Memerlukan autentikasi (JWT token)**
    """
    bookings = service.get_all_bookings()
    return [BookingResponse.from_entity(b) for b in bookings]


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: str,
    service: BookingService = Depends(get_booking_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mengambil detail booking berdasarkan ID
    
    **Memerlukan autentikasi (JWT token)**
    """
    booking = service.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} tidak ditemukan")
    return BookingResponse.from_entity(booking)


@router.post("/{booking_id}/confirm", response_model=BookingResponse)
def confirm_booking(
    booking_id: str,
    request: ConfirmBookingRequest,
    service: BookingService = Depends(get_booking_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Konfirmasi booking oleh trainer
    
    **Memerlukan autentikasi (JWT token)**
    """
    try:
        booking = service.confirm_booking(booking_id, request.trainer_id)
        return BookingResponse.from_entity(booking)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{booking_id}/reject", response_model=BookingResponse)
def reject_booking(
    booking_id: str,
    request: RejectBookingRequest,
    service: BookingService = Depends(get_booking_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Tolak booking oleh trainer
    
    **Memerlukan autentikasi (JWT token)**
    """
    try:
        booking = service.reject_booking(booking_id, request.trainer_id, request.reason)
        return BookingResponse.from_entity(booking)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: str,
    request: CancelBookingRequest,
    service: BookingService = Depends(get_booking_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Batalkan booking oleh client atau trainer
    
    **Memerlukan autentikasi (JWT token)**
    """
    try:
        booking = service.cancel_booking(booking_id, request.user_id, request.reason)
        return BookingResponse.from_entity(booking)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{booking_id}/complete", response_model=BookingResponse)
def complete_booking(
    booking_id: str,
    service: BookingService = Depends(get_booking_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Tandai booking sebagai selesai (completed)
    
    **Memerlukan autentikasi (JWT token)**
    """
    try:
        booking = service.complete_booking(booking_id)
        return BookingResponse.from_entity(booking)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/client/{client_id}", response_model=List[BookingResponse])
def get_bookings_by_client(
    client_id: str,
    service: BookingService = Depends(get_booking_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mengambil semua booking milik client tertentu
    
    **Memerlukan autentikasi (JWT token)**
    """
    bookings = service.get_bookings_by_client(client_id)
    return [BookingResponse.from_entity(b) for b in bookings]


@router.get("/trainer/{trainer_id}", response_model=List[BookingResponse])
def get_bookings_by_trainer(
    trainer_id: str,
    service: BookingService = Depends(get_booking_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mengambil semua booking untuk trainer tertentu
    
    **Memerlukan autentikasi (JWT token)**
    """
    bookings = service.get_bookings_by_trainer(trainer_id)
    return [BookingResponse.from_entity(b) for b in bookings]
