from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Q
from .models import Role, RoleModulePermission
from .serializers import RoleSerializer, RoleModulePermissionSerializer


def _get_admin_profile(user):
    """Helper: returns profile for non-super-admin users."""
    if user.role == 'super_admin':
        return None
    return getattr(user, 'profile', None)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Role.objects.all()

        if user.role == 'super_admin':
            # Super admin can filter by org/site via query params
            org_id = self.request.query_params.get('organization_id')
            site_id = self.request.query_params.get('site_id')
            if org_id:
                queryset = queryset.filter(Q(organization_id=org_id) | Q(organization__isnull=True))
            if site_id:
                queryset = queryset.filter(site_id=site_id)
        else:
            # Normal admin: scoped strictly to their own org + site
            profile = getattr(user, 'profile', None)
            if profile:
                if profile.organization_id:
                    queryset = queryset.filter(organization_id=profile.organization_id)
                if profile.site_id:
                    queryset = queryset.filter(site_id=profile.site_id)
        return queryset

    def create(self, request, *args, **kwargs):
        role_name = request.data.get('role_name') or request.data.get('role')
        if not role_name:
            return super().create(request, *args, **kwargs)

        if request.user.role == 'super_admin':
            # Super admin can specify any org/site
            organization_id = request.data.get('organization_id')
            site_id = request.data.get('site_id')
        else:
            # Normal admin: ALWAYS use their own org/site — cannot override
            profile = getattr(request.user, 'profile', None)
            organization_id = profile.organization_id if profile else None
            site_id = profile.site_id if profile else None

        department_id = request.data.get('department_id')

        defaults = {
            'description': request.data.get('description') or "Created via API mapping"
        }

        enrich_fields = [
            'access_level', 'approval_limit', 'can_create_po', 'can_approve_po',
            'can_manage_vendors', 'can_manage_inventory', 'can_manage_payments',
            'can_manage_contracts', 'can_manage_users', 'can_manage_roles',
            'can_export_reports', 'can_view_analytics', 'is_system_role',
            'role_code', 'dashboard_type', 'cross_dept_access'
        ]
        for f in enrich_fields:
            if f in request.data:
                defaults[f] = request.data[f]

        role, created = Role.objects.get_or_create(
            role_name=role_name,
            organization_id=organization_id,
            site_id=site_id,
            defaults=defaults
        )

        if not created:
            for f, val in defaults.items():
                setattr(role, f, val)
            role.save()

        if department_id:
            from setups.models import RoleAccessMapping
            from organizations.models import Department
            dept = Department.objects.filter(id=department_id).first()
            if dept:
                RoleAccessMapping.objects.update_or_create(
                    role=role,
                    department=dept,
                    defaults={}
                )

        serializer = self.get_serializer(role)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Normal admin cannot move a role to a different site."""
        if request.user.role != 'super_admin':
            # Strip out any attempt to change org/site
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            data.pop('organization_id', None)
            data.pop('site_id', None)
            request._full_data = data
        
        response = super().update(request, *args, **kwargs)
        
        # Update department_id mapping
        department_id = request.data.get('department_id')
        if department_id is not None:
            from setups.models import RoleAccessMapping
            from organizations.models import Department
            role = self.get_object()
            if department_id == "":
                 RoleAccessMapping.objects.filter(role=role, department__isnull=False).delete()
            else:
                 dept = Department.objects.filter(id=department_id).first()
                 if dept:
                     RoleAccessMapping.objects.filter(role=role, department__isnull=False).delete()
                     RoleAccessMapping.objects.create(role=role, department=dept)
                     
        return response


class RoleModulePermissionViewSet(viewsets.ModelViewSet):
    queryset = RoleModulePermission.objects.all()
    serializer_class = RoleModulePermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = RoleModulePermission.objects.all()
        user = self.request.user
        if user.role == 'super_admin':
            return qs
        # Normal admin: only see permissions for roles in their own org + site
        profile = getattr(user, 'profile', None)
        if profile:
            if profile.organization_id:
                qs = qs.filter(role__organization_id=profile.organization_id)
            if user.role == 'admin' and profile.site_id:
                qs = qs.filter(role__site_id=profile.site_id)
        return qs

    def create(self, request, *args, **kwargs):
        """Validate that the role being granted permissions belongs to the admin's site."""
        if request.user.role != 'super_admin':
            role_id = request.data.get('role')
            if role_id:
                profile = getattr(request.user, 'profile', None)
                try:
                    role = Role.objects.get(id=role_id)
                    if profile:
                        if profile.site_id and str(role.site_id) != str(profile.site_id):
                            return Response(
                                {'error': 'You can only set permissions for roles within your own site.'},
                                status=status.HTTP_403_FORBIDDEN
                            )
                        if profile.organization_id and str(role.organization_id) != str(profile.organization_id):
                            return Response(
                                {'error': 'You can only set permissions for roles within your own organization.'},
                                status=status.HTTP_403_FORBIDDEN
                            )
                except Role.DoesNotExist:
                    return Response({'error': 'Role not found.'}, status=status.HTTP_404_NOT_FOUND)
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='sync-routes')
    def sync_routes(self, request):
        role_id = request.data.get('role_id')
        if not role_id:
            return Response({"error": "role_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

        # For normal admin, verify the role belongs to their site
        if request.user.role != 'super_admin':
            profile = getattr(request.user, 'profile', None)
            if profile:
                if profile.site_id and str(role.site_id) != str(profile.site_id):
                    return Response(
                        {'error': 'You can only sync routes for roles within your own site.'},
                        status=status.HTTP_403_FORBIDDEN
                    )

        MODULE_KEYS = [
            'reports:dashboard', 'procurement:indents', 'procurement:rfqs',
            'procurement:rfqs_comparison', 'procurement:rfqs_vendor', 'procurement:rfqs_quote',
            'procurement:orders', 'procurement:vendors', 'procurement:approvals',
            'procurement:items', 'procurement:inventory_master', 'procurement:inventory',
            'procurement:inspections', 'procurement:grn', 'procurement:inventory_issue',
            'procurement:inventory_transfer', 'procurement:inventory_disposal', 'procurement:inventory_rtv',
            'procurement:qc_checklists', 'procurement:billing', 'procurement:billing_approvals',
            'procurement:payment_proposals', 'procurement:payments', 'procurement:budgets',
            'reports:reports', 'reports:inventory_reports', 'reports:invoice_reports',
            'reports:audit_reports', 'reports:ai', 'core:users', 'core:settings',
            'core:workflows', 'core:departments', 'core:documentation', 'core:organizations',
            'core:sites'
        ]

        from django.db import transaction
        from access_control.models import sync_role_access_mapping

        with transaction.atomic():
            for key in MODULE_KEYS:
                RoleModulePermission.objects.get_or_create(
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

        return Response({"message": f"Successfully synced app routes and initialized permissions for role {role.role_name}."})
