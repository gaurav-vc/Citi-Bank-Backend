import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from access_control.models import Role
from users.models import UserProfile

User = get_user_model()

DEMO_USERS = [
    {"role_name": "super_admin", "email": "admin@demo.com", "name": "Super Admin"},
    {"role_name": "site_keeper", "email": "sitekeeper@demo.com", "name": "Site Keeper"},
    {"role_name": "store_keeper", "email": "storekeeper@demo.com", "name": "Store Keeper"},
    {"role_name": "procurement_executive", "email": "procurementexec@demo.com", "name": "Procurement Executive"},
    {"role_name": "procurement_manager", "email": "procurement@demo.com", "name": "Procurement Manager"},
    {"role_name": "finance_executive", "email": "financeexec@demo.com", "name": "Finance Executive"},
    {"role_name": "finance_manager", "email": "financemanager@demo.com", "name": "Finance Manager"},
    {"role_name": "facility_manager", "email": "facilitymanager@demo.com", "name": "Facility Manager"},
    {"role_name": "project_head", "email": "projecthead@demo.com", "name": "Project Head"},
    {"role_name": "cxo_citi", "email": "arvohra87@gmail.com", "name": "CXO Citi"},
    {"role_name": "cxo_emb", "email": "prashantchaurasiy01@gmail.com", "name": "CXO EMB"},
]

class Command(BaseCommand):
    help = "Seed demo users directly into the database with default credentials."

    def handle(self, *args, **options):
        self.stdout.write("=================== Seeding Demo Users ===================")
        password = "admin@123"

        for data in DEMO_USERS:
            email = data["email"]
            name = data["name"]
            role_name = data["role_name"]

            # Ensure the Role exists in Role mappings
            role_obj, _ = Role.objects.get_or_create(
                role_name=role_name,
                defaults={
                    "description": role_name.replace("_", " ").title(),
                    "status": "Active"
                }
            )

            # Get or create the User
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": name,
                    "role": role_name,
                    "is_active": True,
                    "force_password_change": False,
                }
            )

            # Update credentials & attributes
            user.name = name
            user.role = role_name
            user.is_active = True
            user.force_password_change = False
            user.set_password(password)
            user.save()

            # Ensure profile links role & status correctly
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role_obj
            profile.role_name = role_name
            profile.is_active = True
            profile.save()

            status_str = "Created" if created else "Updated"
            self.stdout.write(f"[*] {status_str}: {email} -> Role: {role_name}")

        self.stdout.write(self.style.SUCCESS("=================== Seeding Completed Successfully ==================="))
