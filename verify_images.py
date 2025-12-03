import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from doctors.models import Doctor
from patients.models import Patient

def test_image_generation():
    print("Testing Doctor Image Generation...")
    doctor = Doctor.objects.create(
        name="Dr. Strange",
        phone="1234567890",
        specialty="Magic",
        available_days="Mon,Fri"
    )
    if doctor.image:
        print(f"SUCCESS: Doctor image generated at {doctor.image.url}")
    else:
        print("FAILURE: Doctor image not generated")

    print("\nTesting Patient Image Generation...")
    patient = Patient.objects.create(
        name="Tony Stark",
        age=45,
        gender="M",
        phone="9876543210",
        address="Stark Tower"
    )
    if patient.image:
        print(f"SUCCESS: Patient image generated at {patient.image.url}")
    else:
        print("FAILURE: Patient image not generated")

if __name__ == "__main__":
    test_image_generation()
