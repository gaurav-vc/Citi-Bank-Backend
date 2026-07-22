"""
Seed script to ensure all required procurement roles exist in the database.
Run from backend directory: python scripts/seed_roles.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from access_control.models import Role

REQUIRED_ROLES = [
    {"role_name": "super_admin", "description": "Super Administrator with full system access", "is_system_role": True, "can_create_po": True, "can_approve_po": True, "can_manage_vendors": True, "can_manage_inventory": True, "can_manage_payments": True, "can_manage_contracts": True, "can_manage_users": True, "can_manage_roles": True, "can_export_reports": True, "can_view_analytics": True},
    {"role_name": "client_admin", "description": "Organization Admin with full administrative rights", "is_system_role": True, "can_create_po": True, "can_approve_po": True, "can_manage_vendors": True, "can_manage_inventory": True, "can_manage_payments": True, "can_manage_contracts": True, "can_manage_users": True, "can_manage_roles": True, "can_export_reports": True, "can_view_analytics": True},
    {"role_name": "admin", "description": "Administrator with full local setup and site management controls", "is_system_role": True, "can_create_po": True, "can_approve_po": True, "can_manage_vendors": True, "can_manage_inventory": True, "can_manage_payments": True, "can_manage_contracts": True, "can_manage_users": True, "can_manage_roles": True, "can_export_reports": True, "can_view_analytics": True},
    {"role_name": "site_keeper", "description": "Site Keeper", "can_create_po": False},
    {"role_name": "store_keeper", "description": "Store Keeper", "can_manage_inventory": True},
    {"role_name": "procurement_manager", "description": "Procurement Manager", "can_create_po": True, "can_approve_po": True, "can_manage_vendors": True, "can_manage_contracts": True, "can_export_reports": True, "can_view_analytics": True},
    {"role_name": "finance_executive", "description": "Finance Executive", "can_manage_payments": True},
    {"role_name": "finance_manager", "description": "Finance Manager", "can_manage_payments": True, "can_export_reports": True, "can_view_analytics": True},
    {"role_name": "facility_manager", "description": "Facility Manager"},
    {"role_name": "project_head", "description": "Project Head", "can_view_analytics": True},
    {"role_name": "cxo", "description": "CXO / Executive with high-level access", "is_system_role": True, "can_create_po": True, "can_approve_po": True, "can_manage_vendors": True, "can_manage_inventory": True, "can_manage_payments": True, "can_manage_contracts": True, "can_manage_users": False, "can_manage_roles": False, "can_export_reports": True, "can_view_analytics": True},
    {"role_name": "vendor", "description": "Vendor"},
]

print("=" * 60)
print("Seeding procurement roles...")
print("=" * 60)

created_count = 0
updated_count = 0
skipped_count = 0

for role_data in REQUIRED_ROLES:
    role_name = role_data["role_name"]
    defaults = {k: v for k, v in role_data.items() if k != "role_name"}
    defaults["status"] = "Active"
    
    role, created = Role.objects.get_or_create(
        role_name=role_name,
        defaults=defaults
    )
    
    if created:
        print(f"  [CREATED] {role_name}")
        created_count += 1
    else:
        print(f"  [EXISTS]  {role_name} (id={role.id})")
        skipped_count += 1

print()
print("=" * 60)
print(f"Done! Created: {created_count}, Already existed: {skipped_count}")
print()
print("Current roles in database:")
for r in Role.objects.all().order_by('id').values('id', 'role_name', 'status'):
    print(f"  id={r['id']:3d}  role_name={r['role_name']:<25s}  status={r['status']}")
