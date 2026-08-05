import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from setups.models import RoleAccessMapping

for mapping in RoleAccessMapping.objects.all():
    perms = mapping.permissions
    if not perms: continue
    base_perms = perms.get('procurement:inventory') or perms.get('procurement:material_issue') or {'view': False, 'create': False, 'edit': False, 'delete': False, 'approve': False}
    for key in ['procurement:inventory_issue', 'procurement:inventory_transfer', 'procurement:inventory_disposal']:
        perms[key] = base_perms.copy()
    mapping.permissions = perms
    mapping.save()
    print(f'Updated {mapping.role.role_name}')
print("Done fixing permissions!")
