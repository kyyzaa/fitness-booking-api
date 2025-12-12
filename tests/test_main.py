"""
Unit tests untuk main.py
Test coverage: root endpoint, health check, and application startup
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self):
        """Test GET / endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["status"] == "active"
        assert data["version"] == "1.0.0"
        assert "docs" in data
        assert "authentication" in data
        assert "endpoints" in data
        assert "domain" in data
        assert "aggregate_root" in data
    
    def test_health_check_endpoint(self):
        """Test GET /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "fitness-booking-api"
    
    def test_root_returns_correct_structure(self):
        """Test root endpoint returns correct data structure"""
        response = client.get("/")
        data = response.json()
        
        # Check authentication endpoints
        assert "/auth/register" in data["authentication"]["register"]
        assert "/auth/login" in data["authentication"]["login"]
        assert "/auth/me" in data["authentication"]["me"]
        
        # Check API endpoints
        assert "/bookings" in data["endpoints"]["bookings"]
        assert "/clients" in data["endpoints"]["clients"]
        assert "/trainers" in data["endpoints"]["trainers"]
        
        # Check DDD info
        assert "DDD" in data["domain"]
        assert data["aggregate_root"] == "BookingSession"
