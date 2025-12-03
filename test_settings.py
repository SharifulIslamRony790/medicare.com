import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

User = get_user_model()

def run_test():
    print("Starting Settings Page Test...")
    
    # 1. Create Test User
    username = 'testuser_settings'
    password = 'old_password123'
    email = 'old@example.com'
    
    try:
        user = User.objects.get(username=username)
        user.delete() # Clean up previous run
        print(f"Deleted existing user: {username}")
    except User.DoesNotExist:
        pass

    user = User.objects.create_user(username=username, email=email, password=password)
    print(f"Created user: {username}")

    c = Client()
    
    # 2. Login
    logged_in = c.login(username=username, password=password)
    if logged_in:
        print("Login successful.")
    else:
        print("Login failed.")
        return

    # 3. Test Profile Update
    print("\nTesting Profile Update...")
    new_email = 'new@example.com'
    response = c.post('/settings/', {
        'update_profile': 'true',
        'username': username,
        'email': new_email
    }, follow=True)
    
    if response.status_code == 200:
        user.refresh_from_db()
        if user.email == new_email:
            print("Profile updated successfully (Email changed).")
        else:
            print(f"Profile update failed. Email is {user.email}")
    else:
        print(f"Profile update request failed. Status: {response.status_code}")

    # 4. Test Password Change
    print("\nTesting Password Change...")
    new_password = 'new_password456'
    response = c.post('/settings/', {
        'change_password': 'true',
        'old_password': password,
        'new_password1': new_password,
        'new_password2': new_password # Django form expects confirmation usually, but let's check the form field names if it fails
    }, follow=True)
    
    # Note: The standard PasswordChangeForm uses 'new_password1' and 'new_password1' usually? 
    # Let's check the form fields if this fails. Actually standard is old_password, new_password1, new_password1.
    
    if response.status_code == 200:
        # Try to login with new password
        c.logout()
        logged_in_new = c.login(username=username, password=new_password)
        if logged_in_new:
            print("Password changed successfully (Logged in with new password).")
        else:
            print("Password change failed (Could not login with new password).")
            # Check for form errors in context if possible, but client doesn't easily expose context without response
            # We can check if the old password still works
            if c.login(username=username, password=password):
                 print("Old password still works.")
    else:
        print(f"Password change request failed. Status: {response.status_code}")

if __name__ == '__main__':
    run_test()
