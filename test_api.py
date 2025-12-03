import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()
client = APIClient()

# Test User Creation
if not User.objects.filter(username='testuser').exists():
    user = User.objects.create_user(username='testuser', password='password123', role='doctor')
else:
    user = User.objects.get(username='testuser')

client.force_authenticate(user=user)

# Test Patients API
response = client.post('/api/patients/', {'name': 'John Doe', 'age': 30, 'gender': 'M', 'phone': '1234567890', 'address': '123 St'})
print(f"Create Patient: {response.status_code}")

# Test Doctors API
response = client.post('/api/doctors/', {'name': 'Dr. Smith', 'phone': '0987654321', 'specialty': 'Cardiology', 'available_days': 'Mon,Wed'})
print(f"Create Doctor: {response.status_code}")

# Test Appointments API
# Need IDs from previous steps, but for simplicity just listing
response = client.get('/api/appointments/')
print(f"List Appointments: {response.status_code}")
