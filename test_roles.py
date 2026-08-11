import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from organizations.models import Site, Organization, Department
from access_control.models import Role, RoleModulePermission
from access_control.views import RoleModulePermissionViewSet
from django.db import transaction

def main():
    print("=== Creating New Organization and Site ===")
    
    with transaction.atomic():
        # Create a new Organization
        org, org_created = Organization.objects.get_or_create(
            name="Global Test Org",
            defaults={
                'code': 'GTO',
                'status': 'Active',
                'organization_type': 'Test'
            }
        )
        print(f"[{'Created' if org_created else 'Found'}] Organization: {org.name} (ID: {org.id})")

        # Create a new Site for this Organization
        site, site_created = Site.objects.get_or_create(
            name="Global Test Site",
            organization=org,
            defaults={
                'code': 'GTS-01',
                'status': 'Active'
            }
        )
        print(f"[{'Created' if site_created else 'Found'}] Site: {site.name} (ID: {site.id})")

        # Create a Department for the Site
        dept, dept_created = Department.objects.get_or_create(
            name="Global Testing Dept",
            site=site,
            organization=org,
            defaults={
                'code': 'GTD-01',
                'status': 'Active'
            }
        )
        print(f"[{'Created' if dept_created else 'Found'}] Department: {dept.name} (ID: {dept.id})")


    print(f"\n=== Adding Test Role to Site: {site.name} ===")
    
    role_name = f"Test_Global_Role_{site.id}"
    
    with transaction.atomic():
        role, created = Role.objects.get_or_create(
            role_name=role_name,
            site=site,
            organization=org,
            defaults={
                'description': 'Test role for global permissions check',
                'access_level': 'Site',
                'role_code': f'TEST_{site.id}',
                'status': 'Active'
            }
        )
        
        if created:
            print(f"Created new role: {role.role_name} (ID: {role.id})")
        else:
            print(f"Role already exists: {role.role_name} (ID: {role.id})")

        from setups.models import RoleAccessMapping
        RoleAccessMapping.objects.update_or_create(
            role=role,
            department=dept,
            defaults={}
        )
        print(f"Mapped role {role.role_name} to department {dept.name}")

    print("\n=== Syncing Routes (Initializing Permissions to False) ===")
    # Simulate the sync_routes logic
    MODULE_KEYS = [
        'core:dashboard', 'core:setup', 'core:users', 'core:organizations',
        'core:sites', 'core:departments', 'core:roles', 'core:settings', 'core:workflows',
        'procurement:vendors', 'procurement:items', 'procurement:contracts',
        'procurement:budgets', 'procurement:indents', 'procurement:approvals',
        'procurement:workflows', 'procurement:rfqs', 'procurement:rfqs_compare', 'procurement:orders',
        'procurement:inventory', 'procurement:issue_to_site', 'procurement:inventory_transfer', 
        'procurement:inventory_scrap', 'procurement:inventory_rtv', 'procurement:grn', 'procurement:qc',
        'procurement:billing', 'procurement:billing_approvals', 'procurement:payments', 
        'procurement:payments_proposals', 'procurement:payments_utr', 'procurement:expenses',
        'procurement:reports', 'procurement:reports_spend', 'procurement:reports_inventory', 
        'procurement:reports_invoice', 'procurement:reports_audit', 'procurement:ai'
    ]

    from access_control.models import sync_role_access_mapping
    with transaction.atomic():
        for key in MODULE_KEYS:
            RoleModulePermission.objects.update_or_create(
                role=role,
                module_key=key,
                defaults={
                    'can_view': False,
                    'can_create': False,
                    'can_edit': False,
                    'can_delete': False,
                    'can_approve': False,
                }
            )
        sync_role_access_mapping(role)
    
    print(f"Initialized {len(MODULE_KEYS)} module permissions for role {role.role_name}.")
    
    print("\n=== Checking Created Permissions ===")
    perms = RoleModulePermission.objects.filter(role=role)
    print(f"Total permissions entries found: {perms.count()}")
    for p in perms[:5]:
        print(f" - {p.module_key}: view={p.can_view}, create={p.can_create}")
    if perms.count() > 5:
        print("   ...")
        
    print("\nDone! Global roles permission logic check completed successfully.")

if __name__ == '__main__':
    main()
