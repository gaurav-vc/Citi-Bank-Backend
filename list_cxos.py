import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def list_cxo_users():
    cxos = User.objects.filter(role__icontains='cxo')
    if not cxos.exists():
        print("No users found with 'cxo' in their role.")
    else:
        for u in cxos:
            print(f"User: {u.email} | Role: {u.role} | Active: {u.is_active}")

if __name__ == '__main__':
    list_cxo_users()
