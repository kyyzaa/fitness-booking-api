"""
Main FastAPI Application
Entry point untuk Fitness Booking API
Platform Booking Personal Trainer - Tubes TST
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.repository import (
    InMemoryBookingRepository,
    InMemoryClientRepository,
    InMemoryTrainerRepository,
    InMemoryUserRepository,
    MockSchedulingApi
)
from app.application.services import BookingService, ClientService, TrainerService
from app.api.booking_routes import router as booking_router
from app.api.client_routes import router as client_router
from app.api.trainer_routes import router as trainer_router
from app.api.auth_routes import router as auth_router

# Inisialisasi repositories (In-Memory untuk demo)
booking_repository = InMemoryBookingRepository()
client_repository = InMemoryClientRepository()
trainer_repository = InMemoryTrainerRepository()
user_repository = InMemoryUserRepository()
scheduling_api = MockSchedulingApi()

# Inisialisasi services
booking_service = BookingService(
    booking_repository=booking_repository,
    client_repository=client_repository,
    trainer_repository=trainer_repository,
    scheduling_api=scheduling_api
)
client_service = ClientService(client_repository=client_repository)
trainer_service = TrainerService(trainer_repository=trainer_repository)

# Inisialisasi FastAPI app
app = FastAPI(
    title="Fitness Booking API",
    description="""
    Platform Booking Personal Trainer API
    
    ## Domain
    Platform untuk menghubungkan client dengan personal trainer, memfasilitasi 
    booking session latihan, manajemen jadwal trainer, dan tracking progress workout client.
    
    ## Bounded Context: Booking Context
    API ini mengimplementasikan **Booking Context** dari arsitektur DDD:
    - Mengelola proses pemesanan sesi latihan antara client dan trainer
    - Validasi jadwal dan ketersediaan waktu
    - Manajemen status booking (PENDING, CONFIRMED, CANCELLED, COMPLETED)
    
    ## Authentication
    API ini menggunakan JWT (JSON Web Token) untuk autentikasi:
    - Register user baru di `/auth/register`
    - Login untuk mendapatkan token di `/auth/login`
    - Gunakan token di header: `Authorization: Bearer <token>`
    
    ## Aggregate Root
    **BookingSession**: Entitas utama yang mengelola siklus hidup sesi latihan
    
    ## Entities
    - **Client**: Pengguna yang melakukan booking
    - **Trainer**: Pelatih yang menyediakan layanan
    - **User**: Pengguna sistem dengan autentikasi
    
    ## Value Objects
    - **TimeSlot**: Rentang waktu untuk sesi latihan
    - **SessionDuration**: Durasi sesi (30-120 menit)
    
    ## Tubes TST - ITB 2025
    Implementasi Domain-Driven Design untuk Sistem Booking Personal Trainer
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (untuk development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(booking_router)
app.include_router(client_router)
app.include_router(trainer_router)


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint - Health check dan informasi API
    """
    return {
        "message": "Fitness Booking API - Platform Booking Personal Trainer",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "redoc": "/redoc",
        "authentication": {
            "register": "/auth/register",
            "login": "/auth/login",
            "me": "/auth/me"
        },
        "endpoints": {
            "bookings": "/bookings",
            "clients": "/clients",
            "trainers": "/trainers"
        },
        "domain": "Booking Context (DDD Implementation)",
        "aggregate_root": "BookingSession"
    }


@app.get("/health", tags=["Root"])
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "fitness-booking-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
