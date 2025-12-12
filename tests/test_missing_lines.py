"""
Test untuk missing lines di routes dan services
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import date, time

client = TestClient(app)


class TestMissingLines:
    """Test untuk cover missing lines"""
    
    def test_get_trainer_not_found(self):
        """Test get trainer yang tidak ditemukan - trainer_routes line 120"""
        # Register dan login
        client.post("/auth/register", json={
            "name": "Test User",
            "email": "testmissing@test.com",
            "password": "password123",
            "phone": "08123456789",
            "role": "CLIENT"
        })
        
        login_response = client.post("/auth/login", data={
            "username": "testmissing@test.com",
            "password": "password123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get(
            "/trainers/NONEXISTENT_ID",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
        assert "tidak ditemukan" in response.json()["detail"]
    
    def test_reject_booking_with_wrong_trainer(self):
        """Test reject booking dengan trainer yang salah - booking_routes line 225"""
        # Register trainer
        client.post("/auth/register", json={
            "name": "Trainer Wrong",
            "email": "trainerwrong@test.com",
            "password": "password123",
            "phone": "08123456780",
            "role": "TRAINER",
            "specialization": "Yoga"
        })
        
        # Register client
        client.post("/auth/register", json={
            "name": "Client Test",
            "email": "clientreject@test.com",
            "password": "password123",
            "phone": "08123456781",
            "role": "CLIENT"
        })
        
        # Login sebagai client untuk create booking
        login_client = client.post("/auth/login", data={
            "username": "clientreject@test.com",
            "password": "password123"
        })
        client_token = login_client.json()["access_token"]
        
        # Create booking
        booking_response = client.post("/bookings/",
            headers={"Authorization": f"Bearer {client_token}"},
            json={
                "trainer_id": "TR001",
                "time_slot": {
                    "date": "2024-02-15",
                    "start_time": "10:00",
                    "end_time": "11:00"
                },
                "duration_minutes": 60
            }
        )
        
        if booking_response.status_code == 201:
            booking_id = booking_response.json()["booking_id"]
            
            # Login sebagai trainer lain (wrong trainer)
            login_trainer = client.post("/auth/login", data={
                "username": "trainerwrong@test.com",
                "password": "password123"
            })
            trainer_token = login_trainer.json()["access_token"]
            
            # Coba reject dengan trainer yang salah
            reject_response = client.post(
                f"/bookings/{booking_id}/reject",
                headers={"Authorization": f"Bearer {trainer_token}"},
                json={
                    "trainer_id": "WRONG_TRAINER_ID",
                    "reason": "Tidak tersedia"
                }
            )
            
            # Should get 400 error karena trainer_id tidak sesuai
            assert reject_response.status_code == 400
