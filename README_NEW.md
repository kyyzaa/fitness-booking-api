# 🏋️ Fitness Booking API

![CI/CD](https://github.com/YOUR_USERNAME/fitness-booking-api/workflows/CI/CD%20Pipeline/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/YOUR_USERNAME/fitness-booking-api)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Platform Booking Personal Trainer dengan implementasi **Domain-Driven Design (DDD)** dan **Test-Driven Development (TDD)**

**📚 Tugas Besar - Teknik Software Testing | Institut Teknologi Bandung 2025**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## 🎯 Overview

API untuk menghubungkan **client dengan personal trainer**, memfasilitasi booking session latihan, manajemen jadwal trainer, dan tracking progress workout client. Project ini dibangun menggunakan prinsip **Domain-Driven Design (DDD)** dengan pendekatan **Test-Driven Development (TDD)**, mencapai **>95% test coverage**.

### 🏛️ Domain Model (DDD)

#### **Bounded Context: Booking Context**
Mengelola proses pemesanan sesi latihan antara client dan trainer dengan fitur:
- ✅ Validasi jadwal dan ketersediaan waktu
- ✅ Pencegahan double booking  
- ✅ Manajemen status booking (PENDING, CONFIRMED, CANCELLED, COMPLETED)
- ✅ JWT-based Authentication & Authorization

#### **Aggregate Roots**
- **BookingSession**: Entitas utama mengelola siklus hidup sesi latihan
- **Client**: Profile dan data client
- **Trainer**: Profile dan keahlian trainer
- **User**: Authentication dan role-based access control

#### **Value Objects**
- **TimeSlot**: Validasi slot waktu (date, start_time, end_time)
- **SessionDuration**: Durasi sesi (30-120 menit)

---

## ✨ Features

### Core Features
- 🔐 **Authentication & Authorization** - JWT-based dengan role (CLIENT, TRAINER, ADMIN)
- 📅 **Booking Management** - Create, confirm, cancel, complete bookings
- 👤 **Client Management** - Profile, fitness goals
- 💪 **Trainer Management** - Specialties, certifications, experience
- 🚫 **Double Booking Prevention** - Validasi otomatis overlapping schedules
- ⏰ **Time Slot Validation** - Validasi jadwal dengan value objects

### Technical Features
- ✅ **95%+ Test Coverage** - Comprehensive unit & integration tests
- 🐳 **Docker Support** - Containerized deployment
- 🔄 **CI/CD Pipeline** - GitHub Actions dengan automated testing
- 📊 **API Documentation** - Interactive Swagger UI & ReDoc
- 🔒 **Security** - Password hashing (bcrypt), JWT tokens
- 📝 **Code Quality** - Black, Flake8, isort

---

## 🏗️ Architecture

```
fitness-booking-api/
├── app/
│   ├── domain/              # Domain Layer (DDD)
│   │   ├── entities.py      # Entities (BookingSession, Client, Trainer, User)
│   │   └── value_objects.py # Value Objects (TimeSlot, SessionDuration)
│   ├── application/         # Application Layer
│   │   └── services.py      # Business logic services
│   ├── infrastructure/      # Infrastructure Layer
│   │   └── repository.py    # Repository implementations
│   ├── api/                 # Presentation Layer
│   │   ├── auth_routes.py   # Authentication endpoints
│   │   ├── booking_routes.py
│   │   ├── client_routes.py
│   │   └── trainer_routes.py
│   ├── auth/                # Authentication & Security
│   │   ├── jwt_handler.py   # JWT token management
│   │   └── dependencies.py  # Auth dependencies
│   └── main.py              # FastAPI application
├── tests/                   # Test Suite (95%+ coverage)
│   ├── test_entities.py
│   ├── test_value_objects.py
│   ├── test_jwt_handler.py
│   ├── test_auth_routes.py
│   └── test_booking_routes.py
├── .github/workflows/       # CI/CD
│   └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── pytest.ini
```

### DDD Layers

1. **Domain Layer**: Pure business logic, entities, value objects
2. **Application Layer**: Use cases, business workflows  
3. **Infrastructure Layer**: Database, external APIs, repositories
4. **Presentation Layer**: REST API endpoints (FastAPI)

---

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.115
- **Language**: Python 3.11
- **Authentication**: JWT (python-jose), bcrypt
- **Testing**: pytest, pytest-cov (95%+ coverage)
- **Code Quality**: black, flake8, isort
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Documentation**: Swagger UI, ReDoc

---

## 🚀 Installation

### Prerequisites

- Python 3.11+
- pip
- (Optional) Docker & Docker Compose

### Local Setup

1. **Clone repository**
```bash
git clone https://github.com/YOUR_USERNAME/fitness-booking-api.git
cd fitness-booking-api
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment** (optional)
```bash
cp .env.example .env
# Edit .env with your configurations
```

---

## 🏃 Running the Application

### Method 1: Local Development

```bash
uvicorn app.main:app --reload
```

Server will run at: **http://localhost:8000**

### Method 2: Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

Open `htmlcov/index.html` untuk visual coverage report.

### Run Specific Test Files

```bash
# Domain tests
pytest tests/test_entities.py tests/test_value_objects.py -v

# API tests
pytest tests/test_auth_routes.py tests/test_booking_routes.py -v

# JWT tests
pytest tests/test_jwt_handler.py -v
```

### Test Coverage Target

✅ **Target: 95%+ coverage**

Current coverage includes:
- Domain Layer (entities, value objects)
- Application Layer (services)
- Infrastructure Layer (repositories)
- API Routes (all endpoints)
- Auth & JWT handlers

---

## 📖 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | Login & get JWT token | ❌ |
| GET | `/auth/me` | Get current user info | ✅ |

### Client Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/clients/` | Create new client | ✅ |
| GET | `/clients/` | Get all clients | ✅ |
| GET | `/clients/{id}` | Get client by ID | ✅ |

### Trainer Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/trainers/` | Create new trainer | ✅ |
| GET | `/trainers/` | Get all trainers | ✅ |
| GET | `/trainers/{id}` | Get trainer by ID | ✅ |

### Booking Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/bookings/` | Create booking | ✅ |
| GET | `/bookings/` | Get all bookings | ✅ |
| GET | `/bookings/{id}` | Get booking by ID | ✅ |
| POST | `/bookings/{id}/confirm` | Confirm booking | ✅ |
| POST | `/bookings/{id}/cancel` | Cancel booking | ✅ |
| POST | `/bookings/{id}/complete` | Complete booking | ✅ |
| GET | `/bookings/client/{id}` | Get client's bookings | ✅ |
| GET | `/bookings/trainer/{id}` | Get trainer's bookings | ✅ |

### Example Usage

**1. Register**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "password": "password123",
    "role": "CLIENT"
  }'
```

**2. Login**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -d "username=client@example.com&password=password123"
```

**3. Create Booking** (with token)
```bash
curl -X POST "http://localhost:8000/bookings/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "CL001",
    "trainer_id": "TR001",
    "time_slot": {
      "date": "2025-12-15",
      "start_time": "09:00:00",
      "end_time": "10:00:00"
    },
    "duration_minutes": 60
  }'
```

For complete API documentation with interactive testing, visit: http://localhost:8000/docs

---

## 🌐 Deployment

### Railway

1. Create account at [Railway](https://railway.app)
2. Connect GitHub repository
3. Add environment variables (SECRET_KEY, etc.)
4. Deploy automatically from main branch

### Vercel (Serverless)

1. Install Vercel CLI: `npm i -g vercel`
2. Create `vercel.json`:
```json
{
  "builds": [{"src": "app/main.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "app/main.py"}]
}
```
3. Deploy: `vercel --prod`

### Docker Deployment

```bash
# Build image
docker build -t fitness-booking-api .

# Run container
docker run -d -p 8000:8000 --name fitness-api fitness-booking-api
```

---

## 👥 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Code Quality Standards

- **Test Coverage**: Maintain >95% coverage
- **Code Formatting**: Use `black` and `isort`
- **Linting**: Pass `flake8` checks
- **Tests**: All tests must pass before merge

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Authors

**Tugas Besar - Teknik Software Testing**  
Institut Teknologi Bandung - 2025

---

## 📞 Support

For questions or support:
- 📧 Email: your-email@example.com
- 📝 Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/fitness-booking-api/issues)

---

## 🙏 Acknowledgments

- FastAPI Documentation
- Domain-Driven Design by Eric Evans
- Test-Driven Development by Kent Beck

---

**⭐ Star this repo if you find it helpful!**
