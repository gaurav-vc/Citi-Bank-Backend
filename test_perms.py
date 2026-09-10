import os
import django
import sys
import json

sys.path.append(r"c:\Users\MC VIP\OneDrive\Desktop\CitiBank\Campusspend\backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from users.models import User
from users.serializers import UserSerializer

users = User.objects.all()
for u in users:
    if u.role not in ('super_admin', 'admin', 'client_admin'):
        ser = UserSerializer(u)
        print(f"User: {u.email} | Role: {u.role}")
        print("Perms snippet:", json.dumps(ser.data.get('permissions', {})).strip()[:100])
        print("---")
