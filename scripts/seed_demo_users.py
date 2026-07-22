import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import UserProfile
from access_control.models import Role

User = get_user_model()

demo_users = [
    {"email": "admin@demo.com", "name": "Super Admin", "role": "super_admin", "is_superuser": True, "is_staff": True},
    {"email": "sitekeeper@demo.com", "name": "Site Keeper", "role": "site_keeper", "is_superuser": False, "is_staff": True},
    {"email": "procurement@demo.com", "name": "Procurement Manager", "role": "procurement_manager", "is_superuser": False, "is_staff": True},
    {"email": "procurementexec@demo.com", "name": "Procurement Exec", "role": "procurement_manager", "is_superuser": False, "is_staff": True},
    {"email": "storekeeper@demo.com", "name": "Store Keeper", "role": "store_keeper", "is_superuser": False, "is_staff": True},
    {"email": "facilitymanager@demo.com", "name": "Facility Manager", "role": "facility_manager", "is_superuser": False, "is_staff": True},
    {"email": "projecthead@demo.com", "name": "Project Head", "role": "project_head", "is_superuser": False, "is_staff": True},
    {"email": "financeexec@demo.com", "name": "Finance Executive", "role": "finance_executive", "is_superuser": False, "is_staff": True},
    {"email": "financemanager@demo.com", "name": "Finance Manager", "role": "finance_manager", "is_superuser": False, "is_staff": True},
]

print("Re-seeding demo users with profiles and roles...")

for data in demo_users:
    email = data["email"]
    user = User.objects.filter(email=email).first()
    
    if not user:
        user = User.objects.create_user(
            email=email,
            password="Demo@123",
            name=data["name"],
            role=data["role"],
            is_superuser=data["is_superuser"],
            is_staff=data["is_staff"]
        )
        print(f"✅ Created user: {email}")
    else:
        # Update existing
        user.name = data["name"]
        user.role = data["role"]
        user.is_superuser = data["is_superuser"]
        user.is_staff = data["is_staff"]
        user.set_password("Demo@123")
        user.save()
        print(f"🔄 Updated user: {email}")
        
    # Ensure profile exists and role is linked
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role_name = data["role"]
    db_role = Role.objects.filter(role_name=data["role"]).first()
    if db_role:
        profile.role = db_role
    profile.save()

print("\nDone! Users have been fully updated. You can now log in.")
