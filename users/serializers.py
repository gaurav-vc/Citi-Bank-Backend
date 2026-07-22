from rest_framework import serializers
from .models import User, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    organization_id = serializers.IntegerField(
        source="organization.id",
        read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True
    )
    site_id = serializers.IntegerField(
        source="site.id",
        read_only=True
    )
    site_name = serializers.CharField(
        source="site.name",
        read_only=True
    )
    department_id = serializers.IntegerField(
        source="department.id",
        read_only=True
    )
    department_name = serializers.CharField(
        source="department.name",
        read_only=True
    )

    class Meta:
        model = UserProfile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'department', 'tower', 'is_active', 'created_at', 'updated_at', 'profile', 'permissions', 'force_password_change']

    def get_permissions(self, obj):
        from setups.models import RoleAccessMapping

        # 1. Start with role-level permissions
        role_permissions = {}

        # Try department-specific mapping first (site admin case)
        profile = getattr(obj, 'profile', None)
        dept = getattr(profile, 'department', None) if profile else None
        site = getattr(profile, 'site', None) if profile else None

        if dept:
            dept_mapping = RoleAccessMapping.objects.filter(
                role__role_name=obj.role, department=dept
            ).first()
            if dept_mapping:
                role_permissions = dict(dept_mapping.permissions or {})

        # Fall back to global role mapping
        if not role_permissions:
            global_mapping = RoleAccessMapping.objects.filter(
                role__role_name=obj.role, department=None
            ).first()
            if global_mapping:
                role_permissions = dict(global_mapping.permissions or {})

        # 2. Always ensure core:dashboard is present so user can see the dashboard
        dashboard_perm = {'view': True, 'create': False, 'edit': False, 'modify': False, 'cancel': False, 'delete': False}
        role_permissions.setdefault('core:dashboard', dashboard_perm)

        # 3. If user is super_admin, cxo, admin, or client_admin — return all permissions without filtering
        if obj.role in ('super_admin', 'cxo', 'admin', 'client_admin'):
            return role_permissions

        # 4. Intersect with site's module_configuration if user has a site
        if site and site.module_configuration:
            module_cfg = site.module_configuration  # e.g. { "procurement:vendors": True, ... }

            # Build the allowed feature keys from site module config
            allowed_keys = set()
            for cfg_key, is_enabled in module_cfg.items():
                if is_enabled:
                    allowed_keys.add(cfg_key)
                    if ':' in cfg_key:
                        allowed_keys.add(cfg_key)
                    else:
                        # Short key — add both prefixed variants
                        allowed_keys.add(f'procurement:{cfg_key}')
                        allowed_keys.add(f'core:{cfg_key}')

            # Always allow dashboard regardless of module_configuration
            allowed_keys.update({'core:dashboard', 'procurement:dashboard', 'dashboard'})

            # Only filter if there are actual module restrictions configured
            if allowed_keys and role_permissions:
                filtered = {}
                for perm_key, perms in role_permissions.items():
                    if perm_key in allowed_keys or perm_key == 'core:dashboard':
                        filtered[perm_key] = perms
                # Guarantee dashboard even if filter removed it
                filtered.setdefault('core:dashboard', dashboard_perm)
                return filtered

        return role_permissions

