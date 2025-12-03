import os
import django
import random
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from doctors.models import Doctor

fake = Faker()

specialties = [
    'Cardiology', 'Dermatology', 'Neurology', 'Pediatrics', 
    'Orthopedics', 'Psychiatry', 'Oncology', 'General Practice',
    'Gynecology', 'Ophthalmology'
]

days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

def populate(n=100):
    print(f"Creating {n} doctors...")
    for _ in range(n):
        name = f"Dr. {fake.name()}"
        phone = fake.phone_number()
        specialty = random.choice(specialties)
        
        # Random available days (e.g., "Mon,Wed,Fri")
        num_days = random.randint(2, 5)
        available_days = ",".join(random.sample(days, num_days))
        
        Doctor.objects.create(
            name=name,
            phone=phone,
            specialty=specialty,
            available_days=available_days
        )
    print(f"Successfully created {n} doctors.")

if __name__ == '__main__':
    populate()
