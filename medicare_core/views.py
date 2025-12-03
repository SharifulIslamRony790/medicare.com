from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from prescriptions.models import Prescription

def home(request):
    # Redirect unauthenticated users to patient login portal
    if not request.user.is_authenticated:
        return redirect('patient_login')
    
    context = {
        'patient_count': Patient.objects.count(),
        'doctor_count': Doctor.objects.count(),
        'appointment_count': Appointment.objects.count(),
        'prescription_count': Prescription.objects.count(),
    }
    return render(request, 'home.html', context)

def contact(request):
    return render(request, 'contact.html')

def support(request):
    return render(request, 'support.html')

def privacy(request):
    return render(request, 'privacy.html')
