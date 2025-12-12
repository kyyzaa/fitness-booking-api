"""
Tests for client API routes
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestClientRoutes:
    """Tests untuk client endpoints"""
    
    def test_get_all_clients_unauthorized(self):
        """Test get all clients tanpa auth harus error"""
        response = client.get("/clients/")
        assert response.status_code == 401
    
    def test_get_client_by_id_success(self):
        """Test get client by ID yang sukses"""
        # Register user
        register_response = client.post("/auth/register", json={
            "email": "clientroute@test.com",
            "password": "password123",
            "role": "CLIENT"
        })
        assert register_response.status_code in [200, 201]
        
        # Login untuk dapat token
        login_response = client.post("/auth/login", data={
            "username": "clientroute@test.com",
            "password": "password123"
        })
        token = login_response.json()["access_token"]
        
        # Create client via POST /clients/
        create_response = client.post("/clients/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Test Client",
                "email": "clientroute@test.com",
                "phone": "08123456789"
            }
        )
        assert create_response.status_code == 201
        client_id = create_response.json()["client_id"]
        
        # Get client by ID
        response = client.get(f"/clients/{client_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "clientroute@test.com"
    
    def test_get_nonexistent_client(self):
        """Test get client yang tidak ada"""
        # Register client untuk dapat token
        client.post("/auth/register", json={
            "name": "Test",
            "email": "test_nonexist@test.com",
            "password": "password123",
            "phone": "08123456789",
            "role": "CLIENT"
        })
        
        login_response = client.post("/auth/login", data={
            "username": "test_nonexist@test.com",
            "password": "password123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/clients/NONEXISTENT",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
    
    def test_get_all_clients_success(self):
        """Test get all clients yang sukses"""
        # Register client
        client.post("/auth/register", json={
            "name": "Test",
            "email": "clientlist@test.com",
            "password": "password123",
            "phone": "08123456789",
            "role": "CLIENT"
        })
        
        login_response = client.post("/auth/login", data={
            "username": "clientlist@test.com",
            "password": "password123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/clients/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
