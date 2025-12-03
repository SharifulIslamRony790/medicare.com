from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .serializers import UserSerializer
from .forms import CustomUserCreationForm

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

def login_view(request):
    """Redirect to patient login portal"""
    return redirect('patient_login')

def doctor_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Role validation: only doctors can log in through doctor portal
                if user.role == 'doctor':
                    login(request, user)
                    return redirect('home')
                else:
                    from django.contrib import messages
                    messages.error(request, 'This account is not a doctor account. Please use the appropriate login portal.')
            else:
                from django.contrib import messages
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'doctor_login.html', {'form': form})

def admin_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Role validation: only superusers or users with admin role can log in through admin portal
                if user.is_superuser or user.role == 'admin':
                    login(request, user)
                    return redirect('home')
                else:
                    from django.contrib import messages
                    messages.error(request, 'This account is not an admin account. Please use the appropriate login portal.')
            else:
                from django.contrib import messages
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'admin_login.html', {'form': form})

def admin_signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'admin'
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'admin_signup.html', {'form': form})

def signup_view(request):
    """Redirect to patient signup portal"""
    return redirect('patient_signup')

def patient_login_view(request):
    """Dedicated patient login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            # Role validation: only patients can log in through patient portal
            if user.role == 'patient':
                login(request, user)
                return redirect('home')
            else:
                from django.contrib import messages
                messages.error(request, 'This account is not a patient account. Please use the appropriate login portal.')
        else:
            from django.contrib import messages
            messages.error(request, 'Invalid username or password.')
    return render(request, 'patient_login.html')

def patient_signup_view(request):
    """Dedicated patient signup view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create user with patient role
            user = form.save(commit=False)
            user.role = 'patient'
            user.save()
            
            # Create associated patient profile
            from patients.models import Patient
            Patient.objects.create(
                user=user,
                name=user.username,
                age=form.cleaned_data['age'],
                gender=form.cleaned_data['gender'],
                phone=form.cleaned_data['phone'],
                email=user.email,
                address=form.cleaned_data['address']
            )
            
            login(request, user)
            from django.contrib import messages
            messages.success(request, 'Account created successfully! Welcome to MediCare.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'patient_signup.html', {'form': form})

def doctor_signup_view(request):
    if request.method == 'POST':
        from .forms import DoctorSignupForm
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            # Create user with doctor role
            user = form.save(commit=False)
            user.role = 'doctor'
            user.save()
            
            # Create associated doctor profile
            from doctors.models import Doctor
            Doctor.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                specialty=form.cleaned_data['specialty'],
                phone=form.cleaned_data['phone'],
                available_days=form.cleaned_data['available_days']
            )
            
            login(request, user)
            return redirect('home')
    else:
        from .forms import DoctorSignupForm
        form = DoctorSignupForm()
    return render(request, 'doctor_signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('patient_login')

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def settings_view(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user = request.user
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('settings')
        
        elif 'change_password' in request.POST:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Your password was successfully updated!')
                return redirect('settings')
            else:
                messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'settings.html', {'password_form': form})
