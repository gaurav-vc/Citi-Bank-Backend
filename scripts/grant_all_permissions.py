import os
import sys
import django

# Add the backend directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django if not already in a shell context
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from access_control.models import Role, RoleModulePermission, sync_role_access_mapping

MODULE_KEYS = [
    'core:dashboard',
    'core:setup',
    'core:users',
    'core:organizations',
    'core:sites',
    'core:departments',
    'core:roles',
    'core:settings',
    'procurement:vendors',
    'procurement:items',
    'procurement:contracts',
    'procurement:budgets',
    'procurement:indents',
    'procurement:approvals',
    'procurement:workflows',
    'procurement:rfqs',
    'procurement:rfqs_active',
    'procurement:rfqs_comparison',
    'procurement:rfqs_vendor',
    'procurement:rfqs_quote',
    'procurement:orders',
    'procurement:inventory',
    'procurement:inventory_issue',
    'procurement:inventory_transfer',
    'procurement:inventory_disposal',
    'procurement:inventory_gdn',
    'procurement:inventory_rtv',
    'procurement:grn',
    'procurement:qc',
    'procurement:billing',
    'procurement:billing_approvals',
    'procurement:payments',
    'procurement:expenses',
    'procurement:reports',
    'procurement:ai',
    'procurement:indents_create',
    'procurement:indents_my',
    'procurement:inventory_view',
    'procurement:qc_checklists',
    'procurement:expenses_create',
    'procurement:expenses_my'
]

def grant_all_permissions():
    roles = Role.objects.all()
    count = 0
    for role in roles:
        print(f"Granting permissions for role: {role.role_name}...")
        for key in MODULE_KEYS:
            RoleModulePermission.objects.update_or_create(
                role=role,
                module_key=key,
                defaults={
                    'can_view': True,
                    'can_create': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_approve': True,
                }
            )
        # Sync the RoleAccessMapping for the role so that it gets applied to user's permissions JSON
        try:
            sync_role_access_mapping(role)
        except Exception as e:
            print(f"Warning: Could not sync role mapping for {role.role_name}: {e}")
        count += 1
    
    print(f"✅ Successfully granted all permissions for {count} roles!")

if __name__ == "__main__":
    grant_all_permissions()
