from fastapi.testclient import TestClient
from app.main import app
import json

c = TestClient(app)

# Register client
reg = c.post('/auth/register', json={
    'name': 'Test Client',
    'email': 'debugtest@test.com',
    'password': 'pass123',
    'phone': '08123',
    'role': 'CLIENT'
})

# Login
login = c.post('/auth/login', data={
    'username': 'debugtest@test.com',
    'password': 'pass123'
})
token = login.json()['access_token']

# Get user info
user = c.get('/auth/me', headers={'Authorization': f'Bearer {token}'})
client_id = user.json()['user_id']

# Register trainer
trainer_reg = c.post('/auth/register', json={
    'name': 'Trainer Test',
    'email': 'trainertest@test.com',
    'password': 'pass123',
    'phone': '08999',
    'role': 'TRAINER'
})

# Trainer login
trainer_login = c.post('/auth/login', data={
    'username': 'trainertest@test.com',
    'password': 'pass123'
})
trainer_token = trainer_login.json()['access_token']

# Get trainer info
trainer_user = c.get('/auth/me', headers={'Authorization': f'Bearer {trainer_token}'})
trainer_id = trainer_user.json()['user_id']

# Create booking
booking = c.post('/bookings/', 
    headers={'Authorization': f'Bearer {token}'}, 
    json={
        'client_id': client_id,
        'trainer_id': trainer_id,
        'time_slot': {
            'date': '2025-12-20',
            'start_time': '09:00:00',
            'end_time': '10:00:00'
        },
        'duration_minutes': 60
    }
)

print('Status:', booking.status_code)
print('Response Keys:', list(booking.json().keys()))
print('Response:', json.dumps(booking.json(), indent=2))
