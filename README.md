# Fitness Booking API

Platform Booking Personal Trainer - Implementasi Domain-Driven Design (DDD)

**Tubes TST - Institut Teknologi Bandung 2025**

[![CI Pipeline](https://github.com/kyyzaa/fitness-booking-api/actions/workflows/ci.yml/badge.svg)](https://github.com/kyyzaa/fitness-booking-api/actions/workflows/ci.yml)
[![Test Coverage](https://img.shields.io/badge/coverage-96.15%25-brightgreen)](htmlcov/index.html)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

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

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
# Start the application
docker compose up --build

# Run in background
docker compose up -d --build

# Stop the application
docker compose down

# View logs
docker compose logs -f
```

### Local Development

#### Prerequisites
- Python 3.11 atau lebih tinggi
- pip (Python package manager)
- Docker Desktop (opsional, untuk containerization)

#### Instalasi

1. **Clone repository**
   ```bash
   git clone https://github.com/kyyzaa/fitness-booking-api.git
   cd fitness-booking-api
   ```

2. **Buat virtual environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\Activate.ps1
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (opsional)
   ```bash
   # Windows PowerShell
   $env:SECRET_KEY="fitness-booking-secret-key-change-in-production"
   $env:ALGORITHM="HS256"
   $env:ACCESS_TOKEN_EXPIRE_MINUTES="30"
   
   # Linux/Mac
   export SECRET_KEY="fitness-booking-secret-key-change-in-production"
   export ALGORITHM="HS256"
   export ACCESS_TOKEN_EXPIRE_MINUTES="30"
   ```

5. **Jalankan server**
   ```bash
   # Development mode with hot reload
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Production mode
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

6. **Akses API**
   - 📚 **API Documentation (Swagger)**: http://localhost:8000/docs
   - 📖 **Alternative Documentation (ReDoc)**: http://localhost:8000/redoc
   - ❤️ **Health Check**: http://localhost:8000/health
   - 🏠 **Root**: http://localhost:8000/

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

## 🧪 Testing

### Running Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test categories
pytest tests/test_auth_routes.py -v         # Authentication tests
pytest tests/test_booking_routes.py -v      # Booking tests
pytest tests/test_entities.py -v            # Domain entity tests

# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html

# Open coverage report (Windows)
start htmlcov/index.html
```

### Test Structure
```
tests/
├── conftest.py                 # Test fixtures & configuration
├── test_auth_dependencies.py   # Auth middleware tests
├── test_auth_routes.py        # Authentication endpoints
├── test_booking_routes.py     # Booking API tests
├── test_client_routes.py      # Client API tests
├── test_trainer_routes.py     # Trainer API tests
├── test_entities.py           # Domain entities
├── test_entities_edge_cases.py # Edge case tests
├── test_infrastructure.py     # Repository tests
├── test_jwt_handler.py        # JWT token tests
├── test_main.py               # Main app tests
├── test_services_complete.py  # Service layer tests
├── test_services_edge_cases.py # Service edge cases
├── test_value_objects.py      # Value object tests
└── test_validation_methods.py # Validation tests
```

### Test Coverage: 96.15%
- ✅ **176 tests** across 16 test files
- ✅ **Unit Tests**: Individual components
- ✅ **Integration Tests**: End-to-end workflows
- ✅ **Edge Cases**: Error handling and boundaries
- ✅ **Authentication**: JWT and role-based access

### Code Quality

```bash
# Format code with Black
black app/ tests/

# Sort imports with isort
isort app/ tests/

# Lint with flake8
flake8 app/ --max-line-length=100 --ignore=E203,W503
```

## 🐳 Docker Usage

### Docker Compose (Recommended)

```bash
# Build and start
docker compose up --build

# Run in background
docker compose up -d --build

# View logs
docker compose logs -f

# Stop and remove containers
docker compose down

# Rebuild from scratch
docker compose down
docker system prune -f
docker compose up --build
```

### Standalone Docker

```bash
# Build the image
docker build -t fitness-booking-api .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e SECRET_KEY="your-secret-key" \
  -e ALGORITHM="HS256" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  --name fitness-api \
  fitness-booking-api

# View logs
docker logs -f fitness-api

# Stop container
docker stop fitness-api

# Remove container
docker rm fitness-api
```

### Container Features
- ✅ Multi-stage build for smaller image size
- ✅ Health checks for container orchestration
- ✅ Environment variable configuration
- ✅ Optimized for production deployment
- ✅ Non-root user for security

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

Pipeline otomatis berjalan pada setiap push/PR ke branch `main` atau `develop`:

**Jobs:**
1. **Test & Coverage**
   - Run all 176 tests
   - Generate coverage report (96.15%)
   - Upload coverage to artifacts

2. **Linting**
   - Black code formatting check
   - isort import sorting check
   - Flake8 linting

3. **Docker Build**
   - Build Docker image
   - Verify container health
   - Test Docker Compose setup

4. **Security Scan**
   - Trivy vulnerability scanner
   - Dependency security check

### Pipeline Status
[![CI Pipeline](https://github.com/kyyzaa/fitness-booking-api/actions/workflows/ci.yml/badge.svg)](https://github.com/kyyzaa/fitness-booking-api/actions)

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

## 🔧 Tech Stack

### Backend Framework
- **FastAPI 0.115.6** - Modern, fast web framework
- **Uvicorn 0.32.1** - ASGI server with WebSocket support
- **Pydantic 2.10.3** - Data validation & settings management

### Authentication & Security
- **JWT (python-jose 3.3.0)** - JSON Web Token authentication
- **Passlib + bcrypt** - Password hashing
- **Email Validator 2.3.0** - Email validation

### Testing & Quality
- **pytest 8.3.4** - Testing framework
- **pytest-cov 6.0.0** - Coverage reporting
- **pytest-asyncio 0.24.0** - Async test support
- **httpx 0.28.1** - HTTP client for testing
- **Black 24.10.0** - Code formatter
- **isort 5.13.2** - Import sorter
- **Flake8 7.1.1** - Linting

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **GitHub Actions** - CI/CD pipeline

## 🏗️ Project Structure

```
fitness-booking-api/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD pipeline
├── app/
│   ├── domain/                 # Domain Layer (DDD)
│   │   ├── entities.py         # Aggregates & entities
│   │   └── value_objects.py    # Value objects
│   ├── application/            # Application Layer
│   │   └── services.py         # Business logic & use cases
│   ├── infrastructure/         # Infrastructure Layer
│   │   └── repository.py       # Data persistence
│   ├── api/                    # Presentation Layer
│   │   ├── auth_routes.py      # Authentication endpoints
│   │   ├── booking_routes.py   # Booking endpoints
│   │   ├── client_routes.py    # Client endpoints
│   │   └── trainer_routes.py   # Trainer endpoints
│   ├── auth/                   # Authentication Module
│   │   ├── jwt_handler.py      # JWT management
│   │   └── dependencies.py     # Auth middleware
│   └── main.py                 # Application entry point
├── tests/                      # Test suite (176 tests)
│   ├── conftest.py
│   ├── test_auth_*.py
│   ├── test_booking_*.py
│   ├── test_entities*.py
│   ├── test_services*.py
│   └── ...
├── htmlcov/                    # Coverage reports
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Container orchestration
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── .env.example               # Environment variables template
└── README.md                   # This file
```

## 📊 Performance & Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# API info
curl http://localhost:8000/

# Docker health status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Metrics
- **Response Time**: < 100ms (average)
- **Test Coverage**: 96.15%
- **Test Count**: 176 tests
- **Code Quality**: Formatted with Black, sorted with isort

## 📝 Development Guidelines

### Coding Standards
- Follow **PEP 8** style guide
- Use **Black** for code formatting
- Use **isort** for import sorting
- Maintain **96%+** test coverage
- Write **docstrings** for public methods
- Use **type hints** for function signatures

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and test
pytest tests/ -v
black app/ tests/
isort app/ tests/

# Commit with descriptive message
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/your-feature
```

### Commit Message Convention
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `style:` - Code formatting
- `chore:` - Build/config changes

## 📝 Notes

### Implementation Details
- **In-Memory Storage**: Used for demo/testing (replace with PostgreSQL/MySQL for production)
- **Mock Scheduling API**: Simulated external API (replace with real service)
- **JWT Authentication**: Stateless authentication with 30-minute expiry
- **Role-Based Access**: CLIENT, TRAINER, ADMIN roles with permission checks

### Future Enhancements
- **Database Integration**: PostgreSQL/MySQL/MongoDB
- **Real-time Updates**: WebSocket for booking notifications
- **Payment Integration**: Stripe/PayPal for session payments
- **Email Notifications**: SendGrid/AWS SES for booking confirmations
- **File Upload**: Profile pictures & certifications
- **Analytics Dashboard**: Booking stats & trainer performance
- **Mobile App**: React Native/Flutter companion app

### Production Considerations
- Use production-grade database (PostgreSQL recommended)
- Implement proper logging (structlog/loguru)
- Add rate limiting (slowapi)
- Use Redis for caching
- Implement database migrations (Alembic)
- Add monitoring (Prometheus/Grafana)
- Use secrets management (AWS Secrets Manager/Vault)
- Implement backup strategy
- Add load balancing (Nginx/Traefik)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Contact & Support

- **Repository**: https://github.com/kyyzaa/fitness-booking-api
- **Issues**: https://github.com/kyyzaa/fitness-booking-api/issues
- **Swagger Docs**: http://localhost:8000/docs (when running)

## 👨‍💻 Author

**Khairunnisa Azizah (18223117)**  
Tubes TST - Institut Teknologi Bandung 2025

## 📄 License

Educational project - TST ITB

---

**⭐ Star this repository if you find it helpful!**
