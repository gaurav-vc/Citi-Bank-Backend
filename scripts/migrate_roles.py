import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from access_control.models import Role
from setups.models import RoleAccessMapping
from users.models import User, UserProfile

def migrate():
    print("Starting database migration for roles and RBAC...")
    
    # 1. RENAME site_engineer TO site_manager in access_control Role table
    site_eng_role = Role.objects.filter(role_name='site_engineer').first()
    if site_eng_role:
        site_eng_role.role_name = 'site_manager'
        site_eng_role.description = 'Site Manager'
        site_eng_role.save()
        print("Renamed site_engineer role to site_manager in Role model.")
    else:
        if not Role.objects.filter(role_name='site_manager').exists():
            Role.objects.create(role_name='site_manager', description='Site Manager')
            print("Created site_manager role.")
            
    # Update User model and UserProfile model
    updated_users = User.objects.filter(role='site_engineer').update(role='site_manager')
    print(f"Updated {updated_users} users from site_engineer to site_manager.")
    
    updated_profiles = UserProfile.objects.filter(role_name='site_engineer').update(role_name='site_manager')
    print(f"Updated {updated_profiles} user profiles from site_engineer to site_manager.")
    
    # 2. REMOVE role project_head and facility_manager (Commented out to keep roles active)
    # updated_users_ph = User.objects.filter(role='project_head').update(role='site_manager')
    # updated_users_fm = User.objects.filter(role='facility_manager').update(role='site_manager')
    # print(f"Moved {updated_users_ph} project_head and {updated_users_fm} facility_manager users to site_manager.")
    # 
    # UserProfile.objects.filter(role_name='project_head').update(role_name='site_manager')
    # UserProfile.objects.filter(role_name='facility_manager').update(role_name='site_manager')
    # 
    # deleted_ph, _ = Role.objects.filter(role_name='project_head').delete()
    # deleted_fm, _ = Role.objects.filter(role_name='facility_manager').delete()
    # print(f"Deleted roles: project_head={deleted_ph}, facility_manager={deleted_fm}.")

    # 3. Create or sync RoleAccessMapping for cxo and site_manager
    super_admin_role = Role.objects.filter(role_name='super_admin').first()
    cxo_role = Role.objects.filter(role_name='cxo').first()
    site_manager_role = Role.objects.filter(role_name='site_manager').first()
    
    if not cxo_role:
        cxo_role = Role.objects.create(role_name='cxo', description='CXO Management')
        print("Created Role cxo.")
        
    sa_mapping = RoleAccessMapping.objects.filter(role=super_admin_role).first()
    if sa_mapping:
        cxo_perms = {}
        for key, perms in sa_mapping.permissions.items():
            cxo_perms[key] = {
                'view': perms.get('view', True),
                'create': perms.get('create', True),
                'edit': perms.get('edit', True),
                'delete': False
            }
        RoleAccessMapping.objects.update_or_create(
            role=cxo_role,
            defaults={'permissions': cxo_perms}
        )
        print("Synced RoleAccessMapping for cxo role (same visibility, no delete).")
        
    # Default site manager permissions if no previous site_engineer permissions found
    default_sm_perms = {
        'core:dashboard': {'view': True},
        'procurement:qc': {'view': True, 'create': True, 'edit': True, 'delete': False},
        'procurement:indents': {'view': True, 'create': True, 'edit': True, 'delete': False},
        'procurement:expenses': {'view': True, 'create': True, 'edit': True, 'delete': False},
        'procurement:inventory': {'view': True},
        'procurement:vendors': {'view': True},
        'procurement:approvals': {'view': True}
    }
    
    RoleAccessMapping.objects.update_or_create(
        role=site_manager_role,
        defaults={'permissions': default_sm_perms}
    )
    print("Created/updated permissions mapping for site_manager.")

    print("Role migration and permission sync completed successfully.")

if __name__ == '__main__':
    migrate()
