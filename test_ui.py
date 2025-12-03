import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

client = Client()

urls = [
    'home',
    'patient_list',
    'patient_add',
    'doctor_list',
    'doctor_add',
    'appointment_list',
    'appointment_add',
    'prescription_list',
    'prescription_add',
    'invoice_list',
    'invoice_add',
]

print("Testing UI Endpoints...")
for url_name in urls:
    try:
        url = reverse(url_name)
        response = client.get(url)
        print(f"{url_name}: {response.status_code}")
    except Exception as e:
        print(f"{url_name}: FAILED - {e}")
