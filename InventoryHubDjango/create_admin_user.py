import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_hub.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from django.utils import timezone

# Define user credentials
username = 'admin'
email = 'admin@gmail.com'
password = 'admin123'

# Check if user already exists
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    print(f"User '{username}' already exists. Updating admin privileges.")
else:
    # Create new user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    print(f"Created new user: {username}")

# Set staff privileges (not superuser)
user.is_staff = True
user.is_superuser = False  # Not a superuser, just staff
user.save()

# Create or update UserProfile
if hasattr(user, 'profile'):
    print(f"UserProfile for {username} already exists.")
else:
    UserProfile.objects.create(
        user=user,
        phone='',
        country='',
        state='',
        last_login=timezone.now()
    )
    print(f"Created UserProfile for {username}")

print(f"User '{username}' now has admin privileges.")
print("This user can access admin dashboard and other admin-only areas.") 