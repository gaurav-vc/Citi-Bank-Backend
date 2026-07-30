from django.core.management.base import BaseCommand
from access_control.models import Role
from setups.models import RoleAccessMapping, AppModule, AppFeature

class Command(BaseCommand):
    help = 'Seeds the RoleAccessMapping table with default permissions for all roles'

    def handle(self, *args, **options):
        # 1. Clear existing AppModule and AppFeature records to prevent duplicates and clean old categories
        AppFeature.objects.all().delete()
        AppModule.objects.all().delete()
        self.stdout.write(self.style.WARNING("Cleared existing AppModule and AppFeature records for a clean state."))

        # 2. Seed modules and features matching the correct classification
        modules_data = [
            {
                'name': 'Core Features',
                'order': 0,
                'features': [
                    {'key': 'core:dashboard', 'label': 'Dashboard'},
                    {'key': 'core:users', 'label': 'User Management'},
                    {'key': 'core:organizations', 'label': 'Organizations'},
                    {'key': 'core:sites', 'label': 'Sites'},
                    {'key': 'core:departments', 'label': 'Departments'},
                ]
            },
            {
                'name': 'Procurement',
                'order': 1,
                'features': [
                    {'key': 'procurement:vendors', 'label': 'Vendor Master'},
                    {'key': 'procurement:items', 'label': 'Item/Service Master'},
                    {'key': 'procurement:contracts', 'label': 'Rate Contract/AMC'},
                    {'key': 'procurement:budgets', 'label': 'Budget Master'},
                    {'key': 'procurement:indents', 'label': 'Requisitions/Indents'},
                    {'key': 'procurement:rfqs', 'label': 'Tendering/RFQs'},
                    {'key': 'procurement:orders', 'label': 'Purchase Orders'},
                    {'key': 'procurement:workflows', 'label': 'Workflow Rules'}
                ]
            },
            {
                'name': 'Inventory',
                'order': 2,
                'features': [
                    {'key': 'procurement:inventory_master', 'label': 'Inventory Settings'},
                    {'key': 'procurement:inventory', 'label': 'Inventory Management'},
                    {'key': 'procurement:inspections', 'label': 'Quality Inspection'},
                    {'key': 'procurement:grn', 'label': 'GRN Entry'},
                ]
            },
            {
                'name': 'Quality Inspection',
                'order': 3,
                'features': [
                    {'key': 'procurement:qc', 'label': 'QC & Service Entry'},
                    {'key': 'procurement:qc_checklists', 'label': 'Quality Inspection Checklists'},
                ]
            },
            {
                'name': 'Finance & Billing',
                'order': 4,
                'features': [
                    {'key': 'procurement:billing', 'label': 'Billing Invoices'},
                    {'key': 'procurement:payments', 'label': 'Payment Processing'},
                    {'key': 'procurement:expenses', 'label': 'Expense Management'},
                ]
            },
            {
                'name': 'Reports & Analytics',
                'order': 5,
                'features': [
                    {'key': 'procurement:reports', 'label': 'Analytics Reports'},
                    {'key': 'procurement:ai', 'label': 'AI Spend Insights'}
                ]
            }
        ]

        for mod_info in modules_data:
            mod_obj = AppModule.objects.create(
                name=mod_info['name'],
                module_order=mod_info['order']
            )
            
            for feat_info in mod_info['features']:
                AppFeature.objects.create(
                    feature_key=feat_info['key'],
                    label=feat_info['label'],
                    module=mod_obj
                )
        self.stdout.write(self.style.SUCCESS("Successfully seeded new AppModule and AppFeature records."))

        roles_list = [
            'super_admin', 'client_admin', 'admin', 'site_keeper', 'store_keeper', 'procurement_manager',
            'finance_executive', 'finance_manager', 'facility_manager', 'project_head',
            'cxo', 'vendor', 'procurement_executive', 'cxo_citi', 'cxo_emb'
        ]
        
        write_access_roles = {
            'super_admin', 'client_admin', 'admin', 'cxo', 'procurement_manager', 'finance_manager', 'facility_manager', 'project_head',
            'procurement_executive', 'cxo_citi', 'cxo_emb'
        }
        
        features = [
            'procurement:vendors',
            'procurement:items',
            'procurement:contracts',
            'procurement:budgets',
            'procurement:indents',
            'procurement:rfqs',
            'procurement:orders',
            'procurement:inventory_master',
            'procurement:inventory',
            'procurement:inspections',
            'procurement:grn',
            'procurement:qc',
            'procurement:qc_checklists',
            'procurement:billing',
            'procurement:payments',
            'procurement:expenses',
            'procurement:reports',
            'procurement:ai',
            'core:users',
            'core:organizations',
            'core:sites',
            'core:departments',
            'procurement:workflows'
        ]

        role_permissions_map = {
            'super_admin': {f: {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True} for f in features},
            'client_admin': {f: {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True} for f in features},
            'admin': {f: {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True} for f in features},
            'cxo': {f: {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': True} for f in features},
            
            'finance_executive': {
                'procurement:orders': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False},
                'procurement:billing': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:payments': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:expenses': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False},
                'procurement:indents': {'view': True, 'create': False, 'edit': True, 'delete': False, 'approve': True},
                'procurement:rfqs': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': True},
            },
            
            'finance_manager': {
                'procurement:orders': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': True},
                'procurement:billing': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'procurement:payments': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'procurement:expenses': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'procurement:budgets': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': True},
                'procurement:reports': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False},
                'procurement:indents': {'view': True, 'create': False, 'edit': True, 'delete': False, 'approve': True},
                'procurement:rfqs': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': True},
            },
            
            'site_keeper': {
                'procurement:indents': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:inventory': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False},
                'procurement:expenses': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:items': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False},
                'procurement:inspections': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:grn': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:qc_checklists': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
            },

            'store_keeper': {
                'procurement:indents': {'view': True, 'create': False, 'edit': True, 'delete': False, 'approve': True},
                'procurement:inventory': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:grn': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:items': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False},
                'procurement:qc': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:inspections': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:qc_checklists': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:expenses': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
            },

            'procurement_manager': {
                'procurement:indents': {'view': True, 'create': False, 'edit': True, 'delete': False, 'approve': True},
                'procurement:rfqs': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'procurement:orders': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'procurement:vendors': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'procurement:contracts': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'procurement:reports': {'view': True, 'create': True, 'edit': False, 'delete': False, 'approve': False},
                'procurement:ai': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False},
                'procurement:workflows': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'core:users': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'core:organizations': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'core:sites': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'core:departments': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
            },

            'facility_manager': {
                'procurement:indents': {'view': True, 'create': False, 'edit': True, 'delete': False, 'approve': True},
                'procurement:rfqs': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'procurement:orders': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'procurement:vendors': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'procurement:contracts': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'procurement:reports': {'view': True, 'create': True, 'edit': False, 'delete': False, 'approve': False},
                'procurement:ai': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False},
                'procurement:workflows': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'core:users': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'core:organizations': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'core:sites': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'core:departments': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
            },

            'project_head': {f: {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': True} for f in features},

            'vendor': {
                'procurement:rfqs': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:expenses': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
            },
            
            'procurement_executive': {
                'procurement:rfqs': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True},
                'procurement:indents': {'view': True, 'create': False, 'edit': True, 'delete': False, 'approve': False},
                'procurement:vendors': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False},
                'procurement:items': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False},
            },

            'cxo_citi': {f: {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': True} for f in features},
            'cxo_emb': {f: {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': True} for f in features}
        }
        
        for role_name in roles_list:
            role_obj, created = Role.objects.get_or_create(
                role_name=role_name,
                defaults={'description': f'Default role for {role_name}'}
            )
            
            if role_name in role_permissions_map:
                perms = {}
                for feature in features:
                    perms[feature] = role_permissions_map[role_name].get(feature, {
                        'view': False, 'create': False, 'edit': False, 'delete': False, 'approve': False
                    })
            else:
                is_write_role = role_name in write_access_roles
                perms = {}
                for feature in features:
                    perms[feature] = {
                        'view': True,
                        'create': is_write_role,
                        'edit': is_write_role,
                        'delete': is_write_role,
                        'approve': is_write_role
                    }
            
            mapping, created = RoleAccessMapping.objects.get_or_create(
                role=role_obj,
                department=None,
                defaults={'permissions': perms}
            )
            
            if not created:
                mapping.permissions = perms
                mapping.save()
                self.stdout.write(self.style.SUCCESS(f"Updated permissions mapping for role '{role_name}'"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Created permissions mapping for role '{role_name}'"))
                
        self.stdout.write(self.style.SUCCESS("Successfully seeded all role permissions."))
