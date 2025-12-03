import os
import django
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

User = get_user_model()

class PermissionTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create Users
        self.patient_user = User.objects.create_user(username='patient_perm', password='password123', role='patient')
        self.doctor_user = User.objects.create_user(username='doctor_perm', password='password123', role='doctor')
        
    def test_appointment_access(self):
        print("\n=== Testing Appointment Permissions ===")
        
        # 1. Patient Access
        print("1. Testing Patient Access...")
        self.client.login(username='patient_perm', password='password123')
        response = self.client.get(reverse('appointment_add'))
        if response.status_code == 200:
            print("   [OK] Patient can access appointment booking page.")
        else:
            print(f"   [FAIL] Patient denied access. Status: {response.status_code}")
        self.client.logout()
        
        # 2. Doctor Access
        print("2. Testing Doctor Access...")
        self.client.login(username='doctor_perm', password='password123')
        response = self.client.get(reverse('appointment_add'))
        if response.status_code == 403:
            print("   [OK] Doctor is correctly forbidden (403).")
        else:
            print(f"   [FAIL] Doctor accessed page! Status: {response.status_code}")
            
        print("\n=== Permission Test Completed ===")

if __name__ == '__main__':
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=1)
    failures = test_runner.run_tests(['test_permissions'])
    if failures:
        exit(1)
