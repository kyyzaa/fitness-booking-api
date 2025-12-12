# Fitness Booking API

Platform Booking Personal Trainer - Implementasi Domain-Driven Design (DDD)

**Tubes TST - Institut Teknologi Bandung 2025**

## 📋 Deskripsi

API untuk menghubungkan client dengan personal trainer, memfasilitasi booking session latihan, manajemen jadwal trainer, dan tracking progress workout client.

### Domain Model (DDD)

#### Bounded Context: **Booking Context**
- Mengelola proses pemesanan sesi latihan antara client dan trainer
- Validasi jadwal dan ketersediaan waktu
- Manajemen status booking (PENDING, CONFIRMED, CANCELLED, COMPLETED)

#### Aggregate Root
- **BookingSession**: Entitas utama yang mengelola siklus hidup sesi latihan

#### Entities
- **Client**: Pengguna yang melakukan booking sesi latihan
- **Trainer**: Pelatih yang menyediakan layanan kebugaran
- **User**: Pengguna sistem dengan autentikasi (CLIENT, TRAINER, ADMIN)

#### Value Objects
- **TimeSlot**: Rentang waktu untuk sesi latihan (date, start_time, end_time)
- **SessionDuration**: Durasi sesi dalam menit (30-120 menit)

#### Enumerations
- **BookingStatus**: PENDING, CONFIRMED, CANCELLED, COMPLETED
- **UserRole**: CLIENT, TRAINER, ADMIN

## 🔐 Authentication

API ini dilindungi dengan **JWT (JSON Web Token) Authentication**:
- Semua endpoint (kecuali `/auth/*`) memerlukan autentikasi
- Token berlaku selama 30 menit
- Gunakan header: `Authorization: Bearer <token>`

**Auth Endpoints:**
- `POST /auth/register` - Register user baru
- `POST /auth/login` - Login dan dapatkan JWT token
- `GET /auth/me` - Informasi user yang sedang login

📖 **Panduan lengkap:** Lihat [AUTHENTICATION.md](AUTHENTICATION.md)
🧪 **Testing guide:** Lihat [AUTH_TEST.md](AUTH_TEST.md)

## 🏗️ Arsitektur

Proyek ini mengikuti prinsip **Domain-Driven Design (DDD)**:

```
fitness-booking-api/
├── app/
│   ├── domain/              # Domain Layer (Entities, Value Objects, Aggregates)
│   │   ├── entities.py
│   │   └── value_objects.py
│   ├── application/         # Application Layer (Use Cases, Services)
│   │   └── services.py
│   ├── infrastructure/      # Infrastructure Layer (Repositories)
│   │   └── repository.py
│   ├── api/                 # API/Presentation Layer (Routes, DTOs)
│   │   ├── booking_routes.py
│   │   ├── client_routes.py
│   │   ├── trainer_routes.py
│   │   └── auth_routes.py   # 🔐 Authentication endpoints
│   ├── auth/                # 🔐 Authentication Module
│   │   ├── jwt_handler.py   # JWT token management
│   │   └── dependencies.py  # Auth dependencies & middleware
│   └── main.py             # Entry Point FastAPI
├── requirements.txt
└── README.md
```

## 🚀 Cara Menjalankan

### Prerequisites
- Python 3.10 atau lebih tinggi
- pip (Python package manager)

### Instalasi

1. **Clone/Download repository ini**

2. **Buat virtual environment (opsional tapi direkomendasikan)**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Jalankan server**
   ```powershell
   uvicorn app.main:app --reload
   ```

5. **Akses API**
   - API Documentation (Swagger): http://localhost:8000/docs
   - Alternative Documentation (ReDoc): http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## 📡 API Endpoints

### Root
- `GET /` - Informasi API
- `GET /health` - Health check

### Clients
- `POST /clients` - Buat client baru
- `GET /clients` - List semua clients
- `GET /clients/{client_id}` - Detail client

### Trainers
- `POST /trainers` - Buat trainer baru
- `GET /trainers` - List semua trainers
- `GET /trainers/{trainer_id}` - Detail trainer

### Bookings
- `POST /bookings` - Buat booking baru
- `GET /bookings` - List semua bookings
- `GET /bookings/{booking_id}` - Detail booking
- `POST /bookings/{booking_id}/confirm` - Konfirmasi booking (oleh trainer)
- `POST /bookings/{booking_id}/reject` - Tolak booking (oleh trainer)
- `POST /bookings/{booking_id}/cancel` - Batalkan booking
- `POST /bookings/{booking_id}/complete` - Selesaikan booking
- `GET /bookings/client/{client_id}` - List booking by client
- `GET /bookings/trainer/{trainer_id}` - List booking by trainer

## 🧪 Testing dengan Postman/cURL

### 1. Buat Client
```powershell
curl -X POST "http://localhost:8000/clients" `
  -H "Content-Type: application/json" `
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+6281234567890",
    "fitness_goals": "Weight loss and muscle building"
  }'
```

### 2. Buat Trainer
```powershell
curl -X POST "http://localhost:8000/trainers" `
  -H "Content-Type: application/json" `
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+6281234567891",
    "specialty": "Strength training",
    "certification": "NASM-CPT",
    "experience": 5
  }'
```

### 3. Buat Booking
```powershell
curl -X POST "http://localhost:8000/bookings" `
  -H "Content-Type: application/json" `
  -d '{
    "client_id": "CL<DARI_RESPONSE_1>",
    "trainer_id": "TR<DARI_RESPONSE_2>",
    "time_slot": {
      "date": "2025-11-20",
      "start_time": "09:00:00",
      "end_time": "10:00:00"
    },
    "duration_minutes": 60
  }'
```

### 4. Konfirmasi Booking
```powershell
curl -X POST "http://localhost:8000/bookings/{booking_id}/confirm" `
  -H "Content-Type: application/json" `
  -d '{
    "trainer_id": "TR<ID_TRAINER>"
  }'
```

### 5. List Semua Bookings
```powershell
curl -X GET "http://localhost:8000/bookings"
```

## 📊 Use Cases Utama

1. **Create Booking**: Client membuat booking sesi dengan trainer
   - Validasi client & trainer exists
   - Validasi ketersediaan jadwal (via Scheduling API)
   - Validasi double booking prevention
   - Status awal: PENDING

2. **Confirm Booking**: Trainer mengkonfirmasi booking
   - Hanya trainer terkait yang bisa konfirmasi
   - Status berubah: PENDING → CONFIRMED

3. **Reject Booking**: Trainer menolak booking dengan alasan
   - Status berubah: PENDING → CANCELLED

4. **Cancel Booking**: Client/Trainer membatalkan booking
   - Bisa dilakukan oleh client atau trainer
   - Status berubah: PENDING/CONFIRMED → CANCELLED

5. **Complete Booking**: Menandai sesi selesai
   - Hanya booking CONFIRMED yang bisa diselesaikan
   - Status berubah: CONFIRMED → COMPLETED

## 🔧 Teknologi

- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **In-Memory Storage**: Untuk demo (bisa diganti dengan database real)

## 📝 Catatan Implementasi

- Repository menggunakan **In-Memory storage** untuk simplicity
- Scheduling API menggunakan **Mock implementation**
- Pada production, ganti dengan:
  - Database (PostgreSQL/MySQL) untuk repository
  - Real Scheduling API endpoint
  - Authentication & Authorization
  - Event-driven communication (Kafka/RabbitMQ)

## 🎯 Domain Events (Future Enhancement)

Untuk implementasi lengkap, perlu ditambahkan:
- `BookingConfirmedEvent`: Dikirim setelah booking dikonfirmasi
- `BookingCancelledEvent`: Dikirim saat booking dibatalkan
- Event Publisher/Subscriber mechanism

## 👨‍💻 Author

**Khairunnisa Azizah (18223117)**  
Tubes TST - Institut Teknologi Bandung 2025

## 📄 License

Educational project - TST ITB
