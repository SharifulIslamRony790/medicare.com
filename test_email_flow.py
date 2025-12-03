import os
import django
import sys
from io import StringIO

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from django.test import Client
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from billing.models import Invoice
from django.utils import timezone
import datetime

def run_test():
    print("Starting Email Verification Test...")
    
    # Create Client
    c = Client()

    # 1. Create Test Data
    print("Creating test data...")
    try:
        # Create Patient
        patient, created = Patient.objects.get_or_create(
            name='Test Patient',
            defaults={
                'age': 30,
                'gender': 'M',
                'phone': '1234567890',
                'email': 'mdsharifulislamrony790@gmail.com', # User's email
                'address': '123 Test St'
            }
        )
        if not created:
            patient.email = 'mdsharifulislamrony790@gmail.com'
            patient.save()
        print(f"Patient created: {patient.name} ({patient.email})")

        # Create Doctor
        doctor, created = Doctor.objects.get_or_create(
            name='Dr. Test',
            defaults={
                'specialty': 'General',
                'phone': '0987654321',
                'available_days': 'Mon,Tue,Wed'
            }
        )
        print(f"Doctor created: {doctor.name}")

    except Exception as e:
        print(f"Error creating data: {e}")
        return

    # 2. Test Appointment Email
    print("\nTesting Appointment Confirmation Email...")
    try:
        # Prepare form data
        appointment_data = {
            'patient': patient.id,
            'doctor': doctor.id,
            'date': timezone.now().date() + datetime.timedelta(days=1),
            'time': '10:00',
            'status': 'confirmed'
        }
        
        # Capture stdout to check for error prints from the view
        # The view prints "Error sending email: ..." if it fails
        
        response = c.post('/appointments/add/', appointment_data)
        
        if response.status_code == 302:
            print("Appointment created successfully (Redirected).")
            print("Check your email inbox for Appointment Confirmation.")
        else:
            print(f"Failed to create appointment. Status: {response.status_code}")
            print(response.content.decode())

    except Exception as e:
        print(f"Error testing appointment: {e}")

    # 3. Test Payment Email
    print("\nTesting Payment Receipt Email...")
    try:
        # Create Invoice
        invoice = Invoice.objects.create(
            patient=patient,
            amount=100.00,
            items="Consultation Fee"
        )
        print(f"Invoice created: #{invoice.id}")

        # Process Payment
        # URL: /billing/<id>/pay/<method>/
        payment_url = f'/billing/{invoice.id}/pay/VISA/'
        
        response = c.post(payment_url)
        
        if response.status_code == 302:
            print("Payment processed successfully (Redirected).")
            print("Check your email inbox for Payment Receipt.")
        else:
            print(f"Failed to process payment. Status: {response.status_code}")
            print(response.content.decode())

    except Exception as e:
        print(f"Error testing payment: {e}")

if __name__ == '__main__':
    run_test()
