import os
import django
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import date, time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from prescriptions.models import Prescription

User = get_user_model()

class DoctorFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_doctor_workflow(self):
        print("\n=== Testing Doctor Workflow ===")
        
        # 1. Doctor Signup
        print("1. Testing Doctor Signup...")
        doctor_data = {
            'username': 'dr_house',
            'email': 'house@medicare.com',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
            'name': 'Dr. Gregory House',
            'specialty': 'Diagnostician',
            'phone': '1234567890',
            'available_days': 'Mon,Tue,Wed,Thu,Fri'
        }
        response = self.client.post(reverse('doctor_signup'), doctor_data)
        self.assertEqual(response.status_code, 302) # Should redirect to home
        
        # Verify User and Doctor creation
        doctor_user = User.objects.get(username='dr_house')
        self.assertEqual(doctor_user.role, 'doctor')
        self.assertTrue(hasattr(doctor_user, 'doctor_profile'))
        self.assertEqual(doctor_user.doctor_profile.name, 'Dr. Gregory House')
        print("   Doctor signup successful.")
        
        # 2. Patient Setup (for appointment)
        print("2. Setting up Patient...")
        patient_user = User.objects.create_user(username='patient_john', password='password123', role='patient')
        patient = Patient.objects.create(
            user=patient_user,
            name='John Doe',
            age=30,
            gender='M',
            phone='0987654321',
            address='123 St'
        )
        
        # 3. Create Appointment (as Patient)
        print("3. Booking Appointment...")
        self.client.login(username='patient_john', password='password123')
        appointment_data = {
            'doctor': doctor_user.doctor_profile.id,
            'date': date.today(),
            'time': '10:00'
        }
        response = self.client.post(reverse('appointment_add'), appointment_data)
        self.assertEqual(response.status_code, 302)
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.status, 'pending')
        self.client.logout()
        print("   Appointment booked.")
        
        # 4. Doctor Dashboard & Complete Appointment
        print("4. Testing Doctor Dashboard & Completion...")
        self.client.login(username='dr_house', password='StrongPassword123!')
        
        # Check if doctor sees the appointment
        response = self.client.get(reverse('appointment_list'))
        self.assertContains(response, 'John Doe')
        
        # Complete the appointment
        response = self.client.get(reverse('appointment_complete', args=[appointment.id]))
        self.assertEqual(response.status_code, 302)
        
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'completed')
        print("   Appointment completed.")
        
        # 5. Write Prescription
        print("5. Writing Prescription...")
        prescription_data = {
            'appointment': appointment.id,
            'medicines': 'Vicodin 500mg',
            'advice': 'Take one every 4 hours'
        }
        response = self.client.post(reverse('prescription_add'), prescription_data)
        self.assertEqual(response.status_code, 302)
        
        prescription = Prescription.objects.first()
        self.assertEqual(prescription.medicines, 'Vicodin 500mg')
        self.assertEqual(prescription.appointment, appointment)
        print("   Prescription created.")
        
        print("\n=== Doctor Workflow Verified Successfully! ===")

if __name__ == '__main__':
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=1)
    failures = test_runner.run_tests(['test_doctor_flow'])
    if failures:
        exit(1)
