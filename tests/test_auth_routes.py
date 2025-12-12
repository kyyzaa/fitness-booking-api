"""
Unit tests untuk Auth API Routes
Test coverage: registration, login, user info endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestRegistrationEndpoint:
    """Test /auth/register endpoint"""
    
    def test_register_new_user_success(self):
        """Test registrasi user baru yang sukses"""
        response = client.post("/auth/register", json={
            "email": f"newuser{pytest.timestamp}@example.com",
            "password": "password123",
            "role": "CLIENT"
        })
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert data["email"] == f"newuser{pytest.timestamp}@example.com"
        assert data["role"] == "CLIENT"
        assert data["is_active"] is True
    
    def test_register_with_short_password(self):
        """Test registrasi dengan password terlalu pendek"""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "12345",
            "role": "CLIENT"
        })
        assert response.status_code == 400
        assert "minimal 6 karakter" in response.json()["detail"]
    
    def test_register_with_long_password(self):
        """Test registrasi dengan password terlalu panjang"""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "a" * 73,
            "role": "CLIENT"
        })
        assert response.status_code == 400
        assert "72 bytes" in response.json()["detail"]
    
    def test_register_duplicate_email(self):
        """Test registrasi dengan email yang sudah ada"""
        email = f"duplicate{pytest.timestamp}@example.com"
        
        # Register pertama kali
        response1 = client.post("/auth/register", json={
            "email": email,
            "password": "password123",
            "role": "CLIENT"
        })
        assert response1.status_code == 201
        
        # Register kedua dengan email sama
        response2 = client.post("/auth/register", json={
            "email": email,
            "password": "password456",
            "role": "TRAINER"
        })
        assert response2.status_code == 400
        assert "sudah terdaftar" in response2.json()["detail"]
    
    def test_register_invalid_email(self):
        """Test registrasi dengan email invalid"""
        response = client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "password123",
            "role": "CLIENT"
        })
        assert response.status_code == 422
    
    def test_register_different_roles(self):
        """Test registrasi dengan role berbeda"""
        roles = ["CLIENT", "TRAINER", "ADMIN"]
        
        for role in roles:
            response = client.post("/auth/register", json={
                "email": f"user_{role.lower()}{pytest.timestamp}@example.com",
                "password": "password123",
                "role": role
            })
            assert response.status_code == 201
            assert response.json()["role"] == role
    
    def test_register_missing_fields(self):
        """Test registrasi dengan field yang hilang"""
        # Missing password
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "role": "CLIENT"
        })
        assert response.status_code == 422
        
        # Missing email
        response = client.post("/auth/register", json={
            "password": "password123",
            "role": "CLIENT"
        })
        assert response.status_code == 422


class TestLoginEndpoint:
    """Test /auth/login endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup user untuk testing login"""
        self.test_email = f"loginuser{pytest.timestamp}@example.com"
        self.test_password = "password123"
        
        # Register user
        client.post("/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "role": "CLIENT"
        })
    
    def test_login_success(self):
        """Test login yang sukses"""
        response = client.post("/auth/login", data={
            "username": self.test_email,
            "password": self.test_password
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user_id" in data
        assert data["email"] == self.test_email
        assert data["role"] == "CLIENT"
    
    def test_login_wrong_password(self):
        """Test login dengan password salah"""
        response = client.post("/auth/login", data={
            "username": self.test_email,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "Email atau password salah" in response.json()["detail"]
    
    def test_login_nonexistent_user(self):
        """Test login dengan user yang tidak ada"""
        response = client.post("/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "password123"
        })
        assert response.status_code == 401
    
    def test_login_empty_credentials(self):
        """Test login dengan credentials kosong"""
        response = client.post("/auth/login", data={
            "username": "",
            "password": ""
        })
        assert response.status_code == 422 or response.status_code == 401
    
    def test_login_token_is_valid(self):
        """Test bahwa token yang dihasilkan valid"""
        # Login
        login_response = client.post("/auth/login", data={
            "username": self.test_email,
            "password": self.test_password
        })
        token = login_response.json()["access_token"]
        
        # Use token to access protected endpoint
        response = client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        assert response.json()["email"] == self.test_email
    
    def test_login_case_sensitive_email(self):
        """Test login dengan email case berbeda"""
        response = client.post("/auth/login", data={
            "username": self.test_email.upper(),
            "password": self.test_password
        })
        # Implementation may or may not support case-insensitive emails
        assert response.status_code in [200, 401]


class TestGetCurrentUserEndpoint:
    """Test /auth/me endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup user dan token"""
        self.test_email = f"meuser{pytest.timestamp}@example.com"
        self.test_password = "password123"
        
        # Register
        client.post("/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "role": "TRAINER"
        })
        
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": self.test_email,
            "password": self.test_password
        })
        self.token = login_response.json()["access_token"]
        self.user_id = login_response.json()["user_id"]
    
    def test_get_current_user_success(self):
        """Test mendapatkan info user yang sedang login"""
        response = client.get("/auth/me", headers={
            "Authorization": f"Bearer {self.token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == self.user_id
        assert data["email"] == self.test_email
        assert data["role"] == "TRAINER"
        assert data["is_active"] is True
    
    def test_get_current_user_without_token(self):
        """Test akses tanpa token"""
        response = client.get("/auth/me")
        assert response.status_code == 401 or response.status_code == 403
    
    def test_get_current_user_invalid_token(self):
        """Test dengan token invalid"""
        response = client.get("/auth/me", headers={
            "Authorization": "Bearer invalid.token.here"
        })
        assert response.status_code == 401
    
    def test_get_current_user_malformed_header(self):
        """Test dengan authorization header yang salah format"""
        response = client.get("/auth/me", headers={
            "Authorization": self.token  # Missing "Bearer "
        })
        assert response.status_code == 401 or response.status_code == 403
    
    def test_get_current_user_empty_token(self):
        """Test dengan token kosong"""
        response = client.get("/auth/me", headers={
            "Authorization": "Bearer "
        })
        assert response.status_code == 401


# Setup timestamp untuk unique emails
@pytest.fixture(scope="session", autouse=True)
def set_timestamp():
    """Set unique timestamp untuk test session"""
    import time
    pytest.timestamp = int(time.time())
