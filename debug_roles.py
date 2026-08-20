import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from setups.models import RoleAccessMapping
from access_control.models import Role, RoleModulePermission
from users.models import User

print("--- ROLES ---")
for r in Role.objects.filter(role_name='site_keeper'):
    print(f"ID: {r.id}, Name: {r.role_name}, Org: {r.organization_id}, Site: {r.site_id}")

print("\n--- ROLE ACCESS MAPPINGS ---")
for rm in RoleAccessMapping.objects.filter(role__role_name='site_keeper'):
    dept_name = rm.department.name if rm.department else 'None'
    indents = rm.permissions.get('procurement:indents', {}).get('view')
    rfqs = rm.permissions.get('procurement:rfqs', {}).get('view')
    print(f"Role ID: {rm.role.id}, Dept: {dept_name}, Indents: {indents}, RFQs: {rfqs}")

print("\n--- FIRST 3 SITE KEEPER USERS ---")
for u in User.objects.filter(role='site_keeper')[:3]:
    profile = getattr(u, 'profile', None)
    dept = profile.department.name if profile and profile.department else 'None'
    site = profile.site.id if profile and profile.site else 'None'
    print(f"User: {u.email}, Dept: {dept}, Site: {site}")

print("\n--- RAW MODULE PERMS FOR RFQ ---")
for rmp in RoleModulePermission.objects.filter(role__role_name='site_keeper', module_key='procurement:rfqs'):
    print(f"Role ID: {rmp.role_id}, View: {rmp.can_view}")
