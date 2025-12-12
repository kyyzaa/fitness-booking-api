"""
Unit tests untuk Booking API Routes
Test coverage: create, get, confirm, cancel, complete bookings
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token untuk testing"""
    import time
    email = f"bookingtest{int(time.time())}@example.com"
    
    # Register
    client.post("/auth/register", json={
        "email": email,
        "password": "password123",
        "role": "CLIENT"
    })
    
    # Login
    response = client.post("/auth/login", data={
        "username": email,
        "password": "password123"
    })
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def test_client_id(auth_token):
    """Create test client"""
    response = client.post("/clients/", 
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Test Client",
            "email": "client@test.com",
            "phone": "+6281234567890"
        }
    )
    assert response.status_code == 201, f"Failed to create client: {response.json()}"
    return response.json()["client_id"]


@pytest.fixture(scope="module")
def test_trainer_id(auth_token):
    """Create test trainer"""
    response = client.post("/trainers/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Test Trainer",
            "email": "trainer@test.com",
            "phone": "+6281234567891"
        }
    )
    assert response.status_code == 201, f"Failed to create trainer: {response.json()}"
    return response.json()["trainer_id"]


class TestCreateBooking:
    """Test POST /bookings/ endpoint"""
    
    def test_create_booking_success(self, auth_token, test_client_id, test_trainer_id):
        """Test pembuatan booking yang sukses"""
        response = client.post("/bookings/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "client_id": test_client_id,
                "trainer_id": test_trainer_id,
                "time_slot": {
                    "date": "2025-12-15",
                    "start_time": "09:00:00",
                    "end_time": "10:00:00"
                },
                "duration_minutes": 60
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "booking_id" in data
        assert data["client_id"] == test_client_id
        assert data["trainer_id"] == test_trainer_id
        assert data["status"] == "PENDING"
    
    def test_create_booking_without_auth(self, test_client_id, test_trainer_id):
        """Test create booking tanpa auth token"""
        response = client.post("/bookings/", json={
            "client_id": test_client_id,
            "trainer_id": test_trainer_id,
            "time_slot": {
                "date": "2025-12-15",
                "start_time": "10:00:00",
                "end_time": "11:00:00"
            },
            "duration_minutes": 60
        })
        assert response.status_code in [401, 403]
    
    def test_create_booking_invalid_duration(self, auth_token, test_client_id, test_trainer_id):
        """Test create booking dengan durasi invalid"""
        # Duration < 30
        response = client.post("/bookings/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "client_id": test_client_id,
                "trainer_id": test_trainer_id,
                "time_slot": {
                    "date": "2025-12-15",
                    "start_time": "11:00:00",
                    "end_time": "11:25:00"
                },
                "duration_minutes": 25
            }
        )
        # Implementation returns 400 for validation errors
        assert response.status_code in [400, 422]
    
    def test_create_booking_invalid_time_slot(self, auth_token, test_client_id, test_trainer_id):
        """Test create booking dengan time slot invalid (end before start)"""
        response = client.post("/bookings/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "client_id": test_client_id,
                "trainer_id": test_trainer_id,
                "time_slot": {
                    "date": "2025-12-15",
                    "start_time": "12:00:00",
                    "end_time": "11:00:00"
                },
                "duration_minutes": 60
            }
        )
        # Implementation returns 400 for validation errors
        assert response.status_code in [400, 422]


class TestGetBookings:
    """Test GET bookings endpoints"""
    
    _counter = 0  # Class counter to generate unique slots
    
    @pytest.fixture(autouse=True)
    def setup_booking(self, auth_token, test_client_id, test_trainer_id):
        """Create booking untuk testing"""
        # Use unique time slot based on counter
        TestGetBookings._counter += 1
        hour = 10 + (TestGetBookings._counter % 8)  # Hours 10-17
        minute = (TestGetBookings._counter * 5) % 60  # Minutes 0, 5, 10...
        response = client.post("/bookings/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "client_id": test_client_id,
                "trainer_id": test_trainer_id,
                "time_slot": {
                    "date": "2025-12-20",
                    "start_time": f"{hour:02d}:{minute:02d}:00",
                    "end_time": f"{hour+1:02d}:{minute:02d}:00"
                },
                "duration_minutes": 60
            }
        )
        assert response.status_code == 201, f"Failed to create booking: {response.status_code} - {response.json()}"
        self.booking_id = response.json()["booking_id"]
        self.client_id = test_client_id
        self.trainer_id = test_trainer_id
    
    def test_get_all_bookings(self, auth_token):
        """Test get all bookings"""
        response = client.get("/bookings/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_booking_by_id(self, auth_token):
        """Test get booking by ID"""
        response = client.get(f"/bookings/{self.booking_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["booking_id"] == self.booking_id
    
    def test_get_nonexistent_booking(self, auth_token):
        """Test get booking yang tidak ada"""
        response = client.get("/bookings/NONEXISTENT",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404
    
    def test_get_bookings_by_client(self, auth_token):
        """Test get bookings by client"""
        response = client.get(f"/bookings/client/{self.client_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_bookings_by_trainer(self, auth_token):
        """Test get bookings by trainer"""
        response = client.get(f"/bookings/trainer/{self.trainer_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestBookingActions:
    """Test confirm, cancel, complete booking"""
    
    _counter = 0  # Class counter to generate unique slots
    
    @pytest.fixture(autouse=True)
    def setup_booking(self, auth_token, test_client_id, test_trainer_id):
        """Create fresh booking for each test"""
        # Use unique time slot based on counter
        TestBookingActions._counter += 1
        day = 21 + (TestBookingActions._counter % 5)  # Days 21-25
        hour = 9 + (TestBookingActions._counter % 9)  # Hours 9-17
        response = client.post("/bookings/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "client_id": test_client_id,
                "trainer_id": test_trainer_id,
                "time_slot": {
                    "date": f"2025-12-{day:02d}",
                    "start_time": f"{hour:02d}:00:00",
                    "end_time": f"{hour+1:02d}:00:00"
                },
                "duration_minutes": 60
            }
        )
        assert response.status_code == 201, f"Failed to create booking: {response.status_code} - {response.json()}"
        self.booking_id = response.json()["booking_id"]
        self.client_id = test_client_id
        self.trainer_id = test_trainer_id
    
    def test_confirm_booking(self, auth_token):
        """Test confirm booking"""
        response = client.post(f"/bookings/{self.booking_id}/confirm",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"trainer_id": self.trainer_id}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "CONFIRMED"
    
    def test_cancel_booking(self, auth_token):
        """Test cancel booking"""
        response = client.post(f"/bookings/{self.booking_id}/cancel",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "user_id": self.client_id,
                "reason": "Test cancellation"
            }
        )
        assert response.status_code == 200
        assert response.json()["status"] == "CANCELLED"
    
    def test_complete_booking(self, auth_token):
        """Test complete booking"""
        # First confirm
        client.post(f"/bookings/{self.booking_id}/confirm",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"trainer_id": self.trainer_id}
        )
        
        # Then complete
        response = client.post(f"/bookings/{self.booking_id}/complete",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "COMPLETED"
    
    def test_confirm_nonexistent_booking(self, auth_token):
        """Test confirm booking yang tidak ada"""
        response = client.post("/bookings/NONEXISTENT/confirm",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"trainer_id": self.trainer_id}
        )
        assert response.status_code == 400
    
    def test_reject_nonexistent_booking(self, auth_token):
        """Test reject booking yang tidak ada"""
        response = client.post("/bookings/NONEXISTENT/reject",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"trainer_id": self.trainer_id, "reason": "Test"}
        )
        assert response.status_code == 400
    
    def test_cancel_nonexistent_booking(self, auth_token):
        """Test cancel booking yang tidak ada"""
        response = client.post("/bookings/NONEXISTENT/cancel",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"user_id": self.client_id, "reason": "Test"}
        )
        assert response.status_code == 400
    
    def test_complete_nonexistent_booking(self, auth_token):
        """Test complete booking yang tidak ada"""
        response = client.post("/bookings/NONEXISTENT/complete",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
