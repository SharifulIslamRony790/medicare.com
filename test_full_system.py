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
from billing.models import Invoice, Payment

User = get_user_model()

class FullSystemTest(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_full_workflow(self):
        print("\n=== Testing Full System Workflow ===")
        
        # --- ACTOR: DOCTOR ---
        print("\n[DOCTOR] Signing up...")
        doctor_data = {
            'username': 'dr_strange',
            'email': 'strange@medicare.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'name': 'Dr. Stephen Strange',
            'specialty': 'Neurosurgeon',
            'phone': '1234567890',
            'available_days': 'Mon,Tue,Wed,Thu,Fri'
        }
        self.client.post(reverse('doctor_signup'), doctor_data)
        doctor_user = User.objects.get(username='dr_strange')
        print("   Doctor created.")

        # --- ACTOR: PATIENT ---
        print("\n[PATIENT] Signing up...")
        patient_data = {
            'username': 'patient_peter',
            'email': 'peter@medicare.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'age': 20,
            'gender': 'M',
            'phone': '0987654321',
            'address': 'Queens, NY'
        }
        self.client.post(reverse('signup'), patient_data)
        patient_user = User.objects.get(username='patient_peter')
        print("   Patient created.")

        # --- ACTOR: PATIENT (Booking) ---
        print("\n[PATIENT] Booking Appointment...")
        self.client.login(username='patient_peter', password='StrongPass123!')
        appointment_data = {
            'doctor': doctor_user.doctor_profile.id,
            'date': date.today(),
            'time': '14:00'
        }
        self.client.post(reverse('appointment_add'), appointment_data)
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.status, 'pending')
        print("   Appointment booked (Pending).")
        self.client.logout()

        # --- ACTOR: DOCTOR (Consultation) ---
        print("\n[DOCTOR] Completing Appointment...")
        self.client.login(username='dr_strange', password='StrongPass123!')
        
        # Verify doctor sees appointment
        response = self.client.get(reverse('appointment_list'))
        self.assertContains(response, 'patient_peter')
        
        # Complete appointment
        self.client.get(reverse('appointment_complete', args=[appointment.id]))
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'completed')
        print("   Appointment completed.")

        # Write Prescription
        print("[DOCTOR] Writing Prescription...")
        prescription_data = {
            'appointment': appointment.id,
            'medicines': 'Magic Spell 500mg',
            'advice': 'Cast twice daily'
        }
        self.client.post(reverse('prescription_add'), prescription_data)
        prescription = Prescription.objects.first()
        self.assertIsNotNone(prescription)
        print("   Prescription created.")
        self.client.logout()

        # --- ACTOR: ADMIN (Billing) ---
        print("\n[ADMIN] Generating Invoice...")
        admin_user = User.objects.create_superuser('admin', 'admin@medicare.com', 'adminpass')
        self.client.login(username='admin', password='adminpass')
        
        invoice_data = {
            'patient': patient_user.patient_profile.id,
            'amount': 150.00,
            'items': 'Consultation Fee'
        }
        self.client.post(reverse('invoice_add'), invoice_data)
        invoice = Invoice.objects.first()
        self.assertIsNotNone(invoice)
        self.assertFalse(invoice.is_paid)
        print("   Invoice generated.")
        self.client.logout()

        # --- ACTOR: PATIENT (Payment) ---
        print("\n[PATIENT] Paying Invoice...")
        self.client.login(username='patient_peter', password='StrongPass123!')
        
        # Verify patient sees invoice
        response = self.client.get(reverse('invoice_list'))
        self.assertContains(response, '150.0')
        
        # Process Payment (Simulated)
        payment_url = reverse('payment_process', args=[invoice.id, 'credit_card'])
        self.client.post(payment_url, {'card_number': '1234567812345678', 'expiry': '12/25', 'cvv': '123'})
        
        invoice.refresh_from_db()
        self.assertTrue(invoice.is_paid)
        print("   Invoice paid.")
        
        # Verify Receipt Access
        payment = Payment.objects.first()
        response = self.client.get(reverse('payment_receipt_pdf', args=[payment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        print("   Receipt PDF accessible.")
        
        print("\n=== Full System Workflow Verified Successfully! ===")

if __name__ == '__main__':
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=1)
    failures = test_runner.run_tests(['test_full_system'])
    if failures:
        exit(1)
