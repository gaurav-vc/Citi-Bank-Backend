import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

try:
    django.setup()
except Exception as e:
    print(f"Failed to setup Django. Error: {e}")
    sys.exit(1)

def fix_permissions():
    from access_control.models import Role, RoleModulePermission
    
    roles_to_fix = ['site_keeper', 'store_keeper']
    keys_to_add = ['procurement:inspections', 'procurement:grn', 'procurement:qc', 'procurement:qc_checklists']
    
    for role_name in roles_to_fix:
        # Find the role by role_name
        role = Role.objects.filter(role_name=role_name).first()
        if not role:
            print(f"Role '{role_name}' not found in DB.")
            continue

        for key in keys_to_add:
            perm, created = RoleModulePermission.objects.get_or_create(
                role=role,
                module_key=key,
                defaults={'can_view': True, 'can_create': True, 'can_edit': True, 'can_delete': True, 'can_approve': True}
            )
            if not created:
                perm.can_view = True
                perm.can_create = True
                perm.save()
                print(f"Updated {key} for {role_name}")
            else:
                print(f"Created {key} for {role_name}")
                
    print("\nBackend permissions successfully updated!")

if __name__ == "__main__":
    fix_permissions()
