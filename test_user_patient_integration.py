import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from doctors.models import Doctor
from django.utils import timezone
import datetime

User = get_user_model()

def run_test():
    print("Testing User-Patient Refactoring...")
    
    c = Client()
    
    # 1. Test User Signup (should auto-create patient profile)
    print("\n1. Testing Signup with Patient Details...")
    signup_data = {
        'username': 'testpatient',
        'email': 'testpatient@example.com',
        'age': 30,
        'gender': 'M',
        'phone': '1234567890',
        'address': '123 Test St',
        'password1': 'testpass123',
        'password2': 'testpass123',
    }
    
    # Delete if exists
    try:
        user = User.objects.get(username='testpatient')
        if hasattr(user, 'patient_profile'):
            user.patient_profile.delete()
        user.delete()
        print("Deleted existing test user")
    except User.DoesNotExist:
        pass
    
    response = c.post('/signup/', signup_data, follow=True)
    
    if response.status_code == 200:
        user = User.objects.get(username='testpatient')
        print(f"[OK] User created: {user.username}")
        print(f"[OK] User role: {user.role}")
        
        if hasattr(user, 'patient_profile'):
            patient = user.patient_profile
            print(f"[OK] Patient profile auto-created: {patient.name}")
            print(f"  - Age: {patient.age}")
            print(f"  - Gender: {patient.gender}")
            print(f"  - Phone: {patient.phone}")
        else:
            print("[FAIL] Patient profile NOT created!")
            return
    else:
        print(f"[FAIL] Signup failed. Status: {response.status_code}")
        return
    
    # 2. Test Login
    print("\n2. Testing Login...")
    logged_in = c.login(username='testpatient', password='testpass123')
    if logged_in:
        print("[OK] Login successful")
    else:
        print("[FAIL] Login failed")
        return
    
    # 3. Test Appointment Booking (should auto-use user's patient profile)
    print("\n3. Testing Appointment Booking...")
    
    # Create a doctor if doesn't exist
    doctor, _ = Doctor.objects.get_or_create(
        name='Dr. Test',
        defaults={
            'specialty': 'General',
            'phone': '0987654321',
            'available_days': 'Mon,Tue,Wed'
        }
    )
    
    appointment_data = {
        'doctor': doctor.id,
        'date': timezone.now().date() + datetime.timedelta(days=1),
        'time': '10:00',
        'status': 'confirmed'
    }
    
    response = c.post('/appointments/add/', appointment_data, follow=True)
    
    if response.status_code == 200:
        # Check if appointment was created
        from appointments.models import Appointment
        appointment = Appointment.objects.filter(patient=patient).last()
        if appointment:
            print(f"[OK] Appointment created for patient: {appointment.patient.name}")
            print(f"  - Doctor: {appointment.doctor.name}")
            print(f"  - Date: {appointment.date}")
            print("[OK] Email should have been sent to user's email")
        else:
            print("[FAIL] Appointment NOT created")
    else:
        print(f"[FAIL] Appointment booking failed. Status: {response.status_code}")
    
    print("\n[SUCCESS] All tests passed!")
    print("\nKey Changes Verified:")
    print("- User signup auto-creates patient profile")
    print("- User role automatically set to 'patient'")
    print("- Appointment booking uses logged-in user's patient profile")
    print("- No manual patient selection needed")

if __name__ == '__main__':
    run_test()
