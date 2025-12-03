from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from rest_framework import viewsets
from .models import Appointment
from .serializers import AppointmentSerializer
from .forms import AppointmentForm

from django.core.mail import send_mail
from django.conf import settings

# API ViewSet
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

# UI Views
@login_required
def appointment_list(request):
    # Filter to show only logged-in user's appointments
    if hasattr(request.user, 'patient_profile'):
        appointments = Appointment.objects.filter(patient=request.user.patient_profile).order_by('-date', '-time')
    elif hasattr(request.user, 'doctor_profile'):
        # Doctors see appointments booked with them
        appointments = Appointment.objects.filter(doctor=request.user.doctor_profile).order_by('-date', '-time')
    else:
        # Admin/staff can see all appointments
        appointments = Appointment.objects.all().order_by('-date', '-time')
    return render(request, 'appointment_list.html', {'appointments': appointments})

@login_required
def appointment_complete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    # Only the assigned doctor can complete the appointment
    if hasattr(request.user, 'doctor_profile') and appointment.doctor == request.user.doctor_profile:
        appointment.status = 'completed'
        appointment.save()
        return redirect('appointment_list')
    else:
        # Admin/superuser can also complete
        if request.user.is_superuser or request.user.role in ['admin', 'staff']:
            appointment.status = 'completed'
            appointment.save()
            return redirect('appointment_list')
            
    return redirect('appointment_list')

@login_required
def appointment_add(request):
    # Patients book for themselves, doctors/admin/staff can book for any patient
    is_patient = request.user.role == 'patient'
    can_book_for_others = request.user.is_superuser or request.user.role in ['admin', 'staff', 'doctor']
    
    if not (is_patient or can_book_for_others):
        return HttpResponseForbidden("You don't have permission to book appointments.")
        
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            # If patient is booking, auto-set patient from logged-in user
            if is_patient:
                appointment.patient = request.user.patient_profile
            # Otherwise, admin/doctor selected patient from the form
            appointment.save()
            
            # Send Email Notification TO User
            if appointment.status == 'confirmed' and appointment.patient.email:
                subject = 'Appointment Confirmed - MediCare'
                message = f"""
                Dear {appointment.patient.name},

                Your appointment has been confirmed.

                Doctor: {appointment.doctor.name}
                Date: {appointment.date}
                Time: {appointment.time}

                Thank you for choosing MediCare.
                """
                try:
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [appointment.patient.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Error sending email: {e}")

            return redirect('appointment_list')
    else:
        form = AppointmentForm()
        # For patients, exclude the patient field (they book for themselves)
        if is_patient:
            form.fields.pop('patient', None)
    
    return render(request, 'appointment_form.html', {'form': form})
