#!/usr/bin/env python
"""
Script to create a superuser for the Django application.
"""
import os
import sys
import django
from django.conf import settings
from django.contrib.auth.models import User

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

def create_superuser():
    """Create a superuser if it doesn't exist"""
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123'
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f'Superuser "{username}" created successfully!')
        print(f'Email: {email}')
        print(f'Password: {password}')
        print('Please change the password after first login.')
    else:
        print(f'Superuser "{username}" already exists.')

if __name__ == '__main__':
    create_superuser()
