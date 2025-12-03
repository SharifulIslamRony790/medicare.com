from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from rest_framework import viewsets
from .models import Doctor
from .serializers import DoctorSerializer
from .forms import DoctorForm

# API ViewSet
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

# UI Views
def doctor_list(request):
    # All users can see doctor list (patients need to select doctors)
    doctors = Doctor.objects.all()
    return render(request, 'doctor_list.html', {'doctors': doctors})

@login_required
def doctor_add(request):
    # Only admin/superuser/staff can add doctors
    if not (request.user.is_superuser or request.user.role in ['admin', 'staff']):
        return HttpResponseForbidden("You don't have permission to access this page.")
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('doctor_list')
    else:
        form = DoctorForm()
    return render(request, 'doctor_form.html', {'form': form})
