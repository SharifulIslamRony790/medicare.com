from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from rest_framework import viewsets
from .models import Patient
from .serializers import PatientSerializer
from .forms import PatientForm

# API ViewSet
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

# UI Views
@login_required
def patient_list(request):
    # Admin/superuser, staff, and doctors can see patient list
    if not (request.user.is_superuser or request.user.role in ['admin', 'staff', 'doctor']):
        return HttpResponseForbidden("You don't have permission to access this page.")
    patients = Patient.objects.all().order_by('-created_at')
    return render(request, 'patient_list.html', {'patients': patients})

@login_required
def patient_add(request):
    # Admin/superuser, staff, and doctors can add patients
    if not (request.user.is_superuser or request.user.role in ['admin', 'staff', 'doctor']):
        return HttpResponseForbidden("You don't have permission to access this page.")
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'patient_form.html', {'form': form})

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    # Users can only see their own patient profile, admin/superuser/staff/doctors can see all
    if hasattr(request.user, 'patient_profile'):
        if patient != request.user.patient_profile and not (request.user.is_superuser or request.user.role in ['admin', 'staff', 'doctor']):
            return HttpResponseForbidden("You don't have permission to access this page.")
    return render(request, 'patient_detail.html', {'patient': patient})
