import secrets
import string
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from access_control.permissions import RBACPermission
from .models import Organization, Site, Department, SiteModuleAccess
from .serializers import (
    OrganizationSerializer, SiteSerializer, DepartmentSerializer,
    SiteModuleAccessSerializer
)

# Maps module_configuration keys (from site creation) to RBAC permission keys
MODULE_CONFIG_TO_PERMISSION_KEYS = {
    'procurement:dashboard': 'core:dashboard',
    'core:dashboard': 'core:dashboard',
    'dashboard': 'core:dashboard',
    'core:organizations': 'core:organizations',
    'organizations': 'core:organizations',
    'core:sites': 'core:sites',
    'sites': 'core:sites',
    'core:departments': 'core:departments',
    'departments': 'core:departments',
    'core:users': 'core:users',
    'users': 'core:users',
    'procurement:vendors': 'procurement:vendors',
    'vendors': 'procurement:vendors',
    'procurement:indents': 'procurement:indents',
    'indents': 'procurement:indents',
    'procurement:rfqs': 'procurement:rfqs',
    'rfqs': 'procurement:rfqs',
    'procurement:orders': 'procurement:orders',
    'orders': 'procurement:orders',
    'procurement:contracts': 'procurement:contracts',
    'contracts': 'procurement:contracts',
    'procurement:inventory': 'procurement:inventory',
    'inventory': 'procurement:inventory',
    'procurement:grn': 'procurement:grn',
    'grn': 'procurement:grn',
    'procurement:budgets': 'procurement:budgets',
    'budgets': 'procurement:budgets',
    'procurement:expenses': 'procurement:expenses',
    'expenses': 'procurement:expenses',
    'procurement:billing': 'procurement:billing',
    'billing': 'procurement:billing',
    'procurement:payments': 'procurement:payments',
    'payments': 'procurement:payments',
    'procurement:reports': 'procurement:reports',
    'reports': 'procurement:reports',
    'procurement:approvals': 'procurement:approvals',
    'approvals': 'procurement:approvals',
    'procurement:workflows': 'procurement:workflows',
    'workflows': 'procurement:workflows',
    'procurement:ai': 'procurement:ai',
    'ai': 'procurement:ai',
}

# Default permissions granted per module key when a module is enabled
DEFAULT_MODULE_PERMISSIONS = {
    'view': True,
    'create': True,
    'edit': True,
    'modify': True,
    'cancel': False,
    'delete': False,
}

# Restricted-only permissions for sensitive modules
RESTRICTED_MODULE_PERMISSIONS = {
    'view': True,
    'create': False,
    'edit': False,
    'modify': False,
    'cancel': False,
    'delete': False,
}

RESTRICTED_KEYS = {'core:organizations', 'core:sites', 'core:departments', 'core:users'}


def generate_password(length=12):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + '!@#$'
    # Ensure at least one of each type
    pwd = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice('!@#$'),
    ]
    pwd += [secrets.choice(alphabet) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(pwd)
    return ''.join(pwd)


def build_permissions_from_module_config(module_configuration: dict) -> dict:
    """
    Convert a site's module_configuration dict (key -> bool) into
    a RBAC permissions dict (feature_key -> {view, create, edit, ...}).
    """
    permissions = {}
    for config_key, is_enabled in module_configuration.items():
        if not is_enabled:
            continue
        # Normalize the key
        perm_key = MODULE_CONFIG_TO_PERMISSION_KEYS.get(config_key, config_key)
        if perm_key in RESTRICTED_KEYS:
            permissions[perm_key] = dict(RESTRICTED_MODULE_PERMISSIONS)
        else:
            permissions[perm_key] = dict(DEFAULT_MODULE_PERMISSIONS)
    return permissions





class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, RBACPermission]


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated, RBACPermission]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_queryset(self):
        user = self.request.user
        qs = Department.objects.all()

        if user.role == 'super_admin':
            # Super admin can filter by org or site via query params
            org_id = self.request.query_params.get('organization_id')
            site_id = self.request.query_params.get('site_id')
            if site_id:
                qs = qs.filter(site_id=site_id)
            elif org_id:
                qs = qs.filter(site__organization_id=org_id)
        elif user.role in ('admin', 'client_admin'):
            # Scoped to their own site
            profile = getattr(user, 'profile', None)
            if profile and profile.site_id:
                qs = qs.filter(site_id=profile.site_id)
            elif profile and profile.organization_id:
                # client_admin: show all departments for their org
                qs = qs.filter(site__organization_id=profile.organization_id)
        return qs

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        if user.role != 'super_admin':
            # Normal admin: ALWAYS force site_id from their profile — no overrides
            profile = getattr(user, 'profile', None)
            if profile and profile.site_id:
                data['site'] = profile.site_id
                data['site_id'] = profile.site_id
            elif profile and profile.organization_id and user.role == 'client_admin':
                # client_admin without explicit site — allow them to specify a site within their org
                site_id = data.get('site') or data.get('site_id')
                if site_id:
                    from organizations.models import Site as SiteModel
                    site_exists = SiteModel.objects.filter(
                        id=site_id,
                        organization_id=profile.organization_id
                    ).exists()
                    if not site_exists:
                        return Response(
                            {'error': 'You can only create departments for sites within your organization.'},
                            status=status.HTTP_403_FORBIDDEN
                        )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        # get_object() uses get_queryset() scope — admin can't touch other sites' depts
        instance = self.get_object()
        user = request.user
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        if user.role != 'super_admin':
            # Strip any attempt to move dept to a different site
            data.pop('site', None)
            data.pop('site_id', None)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class SiteModuleAccessViewSet(viewsets.ModelViewSet):
    queryset = SiteModuleAccess.objects.all()
    serializer_class = SiteModuleAccessSerializer
    permission_classes = [IsAuthenticated, RBACPermission]


# Human-readable role labels for email
ROLE_LABELS = {
    'super_admin': 'Super Admin',
    'cxo': 'CXO / Management',
    'procurement_manager': 'Procurement Manager',
    'procurement_executive': 'Procurement Executive',
    'finance_manager': 'Finance Manager',
    'finance_executive': 'Finance Executive',
    'facility_manager': 'Facility Manager',
    'site_engineer': 'Site Engineer',
    'store_keeper': 'Store Keeper',
    'project_head': 'Project Head',
}


class SiteAdminProvisionView(APIView):
    """
    Provision a site admin user account when a site is created.

    POST /api/provision-site-admin/
    Body: {
        site_id: int,
        admin_name: str,
        admin_email: str,
        admin_role: str (optional, defaults to 'facility_manager'),
        module_configuration: dict   (key -> bool)
    }

    Creates or updates the user, assigns them to the site, generates
    a random password, builds RBAC permissions from module_configuration,
    and sends a welcome email with login credentials.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        site_id = request.data.get('site_id')
        admin_name = (request.data.get('admin_name') or '').strip()
        admin_email = (request.data.get('admin_email') or '').strip().lower()
        admin_role = (request.data.get('admin_role') or 'facility_manager').strip()
        module_configuration = request.data.get('module_configuration') or {}

        # Validation checks
        requester_role = request.user.role if request.user and request.user.is_authenticated else None
        if admin_role == 'super_admin' and requester_role != 'super_admin':
            return Response({'error': 'Only Super Admin can provision a Super Admin.'}, status=status.HTTP_403_FORBIDDEN)
        if admin_role == 'client_admin' and requester_role != 'super_admin':
            return Response({'error': 'Only Super Admin can provision an Organization Admin.'}, status=status.HTTP_403_FORBIDDEN)

        # Validate required fields
        if not site_id:
            return Response({'error': 'site_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not admin_email:
            return Response({'error': 'admin_email is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not admin_name:
            return Response({'error': 'admin_name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        import re
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', admin_email):
            return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch site
        try:
            site = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            return Response({'error': f'Site {site_id} not found'}, status=status.HTTP_404_NOT_FOUND)

        org = site.organization

        # Imports
        from users.models import User, UserProfile
        from access_control.models import Role

        # Generate a temp password
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        temp_password = ''.join(secrets.choice(alphabet) for i in range(12))

        # Get or create the role
        role_obj, _ = Role.objects.get_or_create(
            role_name=admin_role,
            defaults={'description': ROLE_LABELS.get(admin_role, admin_role.replace('_', ' ').title()), 'status': 'Active'}
        )

        # Create or update the User
        user_created = False
        user = User.objects.filter(email=admin_email).first()
        if user:
            # Update existing user — refresh role and password
            user.name = admin_name
            user.role = admin_role
            user.is_active = True
            print("PASSWORD USED:", temp_password)
            user.set_password(temp_password)
            user.force_password_change = False
            user.save()
        else:
            # Create new user
            print("PASSWORD USED:", temp_password)
            user = User.objects.create_user(
                email=admin_email,
                name=admin_name,
                role=admin_role,
                password=temp_password,
            )
            user.force_password_change = False
            user.save()
            user_created = True

        # Create or update UserProfile â€” link to site, org, role
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.organization = org
        profile.site = site
        profile.role = role_obj
        profile.role_name = admin_role
        profile.is_active = True
        profile.save()

        # Build RBAC permissions from module_configuration
        # Always grant core:dashboard so user can see the dashboard
        effective_module_config = dict(module_configuration)
        effective_module_config.setdefault('core:dashboard', True)
        effective_module_config.setdefault('dashboard', True)

        permissions = build_permissions_from_module_config(effective_module_config)

        # Persist in RoleAccessMapping â€” use site+user specific approach:
        # We store a per-site permission under the user's profile's dept if available,
        # AND update global role mapping so the serializer can find it.
        from setups.models import RoleAccessMapping

        dept = Department.objects.filter(site=site).first()
        if dept:
            RoleAccessMapping.objects.update_or_create(
                role=role_obj,
                department=dept,
                defaults={'permissions': permissions}
            )

        # Global mapping â€” this is what get_permissions() reads by default
        RoleAccessMapping.objects.update_or_create(
            role=role_obj,
            department=None,
            defaults={'permissions': permissions}
        )

        # Update site's module_configuration to include dashboard
        site.module_configuration = effective_module_config
        site.save(update_fields=['module_configuration'])

        # Human-readable role label for email
        role_label = ROLE_LABELS.get(admin_role, admin_role.replace('_', ' ').title())

        # Attempt to send welcome email
        email_sent = False
        try:
            from utils.email_helper import send_onboarding_email
            send_onboarding_email(
                email=admin_email,
                name=admin_name,
                password=temp_password,
                role=role_label,
                org_name=org.name,
                site_name=site.name
            )
            email_sent = True
        except Exception as e:
            print("[EMAIL ERROR]: Failed to send Welcome Email to Organization Admin:", e)

        # Detect if we're using the console backend (dev mode)
        from django.conf import settings as django_settings
        using_console = 'console' in getattr(django_settings, 'EMAIL_BACKEND', '')
        if using_console:
            email_sent = True  # Console backend always "delivers" (to terminal)

        response_data = {
            'success': True,
            'user_created': user_created,
            'email_sent': email_sent,
            'admin_email': admin_email,
            'admin_role': admin_role,
            'role_label': role_label,
            'site_name': site.name,
            'org_name': org.name,
            'permissions_count': len(permissions),
            'temp_password': temp_password,  # always included for super admin reference
            'console_mode': using_console,
        }

        if not email_sent:
            response_data['warning'] = (
                'Email delivery failed â€” configure EMAIL_HOST_PASSWORD in backend/.env '
                'with your Resend API key. Share the temp_password manually.'
            )

        return Response(response_data, status=status.HTTP_201_CREATED)

