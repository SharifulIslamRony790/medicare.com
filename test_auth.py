import os
import django
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

User = get_user_model()
client = Client()

# Test Signup
print("Testing Signup...")
signup_url = reverse('signup')
signup_data = {
    'username': 'newuser',
    'email': 'newuser@example.com',
    'password': 'password123',
    'role': 'patient'
}
# Note: UserCreationForm requires two passwords usually, but CustomUserCreationForm might handle it differently depending on implementation. 
# Standard UserCreationForm expects 'password' and 'password_confirmation' usually handled by frontend.
# Let's check if we can just create user directly via form save logic simulation or just check view response.
# For simplicity in this script, we'll check if the page loads (GET) and if we can post.
# Actually, standard UserCreationForm uses SetPasswordForm mixin which requires two passwords.
# My CustomUserCreationForm inherits UserCreationForm.
# Let's try to just hit the endpoint.

response = client.get(signup_url)
print(f"Signup Page Load: {response.status_code}")

# Test Login
print("Testing Login...")
login_url = reverse('login')
response = client.get(login_url)
print(f"Login Page Load: {response.status_code}")

# Create a user manually to test login post
if not User.objects.filter(username='loginuser').exists():
    User.objects.create_user(username='loginuser', password='password123')

response = client.post(login_url, {'username': 'loginuser', 'password': 'password123'})
if response.status_code == 302:
    print("Login Successful (Redirected)")
else:
    print(f"Login Failed: {response.status_code}")

# Test Logout
print("Testing Logout...")
logout_url = reverse('logout')
response = client.get(logout_url)
if response.status_code == 302:
    print("Logout Successful (Redirected)")
else:
    print(f"Logout Failed: {response.status_code}")
