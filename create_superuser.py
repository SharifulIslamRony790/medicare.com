import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'medicare12@gmail.com'
password = 'admin1234'
email = 'medicare12@gmail.com'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.email = email
    user.is_superuser = True
    user.is_staff = True
    user.role = 'admin'
    user.save()
    print(f"Updated user '{username}' with new password.")
except User.DoesNotExist:
    User.objects.create_superuser(username=username, email=email, password=password, role='admin')
    print(f"Created superuser '{username}'.")
