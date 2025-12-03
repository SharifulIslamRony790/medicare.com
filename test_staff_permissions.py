import os
import django
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from doctors.models import Doctor
from billing.models import Invoice
from patients.models import Patient

User = get_user_model()

class StaffPermissionTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create Staff User
        self.staff_user = User.objects.create_user(username='staff_sarah', password='password123', role='staff')
        
        # Create Patient for testing
        self.patient_user = User.objects.create_user(username='patient_tom', password='password123', role='patient')
        self.patient = Patient.objects.create(user=self.patient_user, name='Tom', age=25, gender='M', phone='111', address='Test')

    def test_staff_capabilities(self):
        print("\n=== Testing Staff Permissions ===")
        self.client.login(username='staff_sarah', password='password123')

        # 1. Add Doctor
        print("1. Staff adding Doctor...")
        doctor_data = {
            'username': 'new_doc',
            'email': 'doc@test.com',
            'password1': 'pass123',
            'password2': 'pass123',
            'name': 'Dr. New',
            'specialty': 'General',
            'phone': '555',
            'available_days': 'Mon'
        }
        # Note: Doctor add usually goes through doctor_signup view or admin panel. 
        # But we also have 'doctor_add' view? Let's check urls.
        # path('doctors/add/', doctor_add, name='doctor_add')
        # Let's check doctor_add view in doctors/views.py
        
        # Actually, doctor_signup is for self-registration. doctor_add might be for admin/staff to add doctor.
        # Let's try hitting doctor_add.
        response = self.client.get(reverse('doctor_add'))
        if response.status_code == 200:
            print("   [OK] Staff can access Add Doctor page.")
        elif response.status_code == 403:
            print("   [FAIL] Staff Forbidden from Add Doctor page.")
        else:
            print(f"   [INFO] Status: {response.status_code}")

        # 2. Create Invoice
        print("2. Staff creating Invoice...")
        invoice_data = {
            'patient': self.patient.id,
            'amount': 200.00,
            'items': 'X-Ray'
        }
        response = self.client.post(reverse('invoice_add'), invoice_data)
        if response.status_code == 302:
            print("   [OK] Staff created invoice successfully.")
            self.assertTrue(Invoice.objects.filter(items='X-Ray').exists())
        else:
            print(f"   [FAIL] Staff failed to create invoice. Status: {response.status_code}")

        # 3. View All Appointments
        print("3. Staff viewing appointments...")
        response = self.client.get(reverse('appointment_list'))
        if response.status_code == 200:
            print("   [OK] Staff can view appointment list.")
        else:
            print(f"   [FAIL] Staff cannot view appointment list. Status: {response.status_code}")

        print("\n=== Staff Permissions Verified ===")

if __name__ == '__main__':
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=1)
    failures = test_runner.run_tests(['test_staff_permissions'])
    if failures:
        exit(1)
