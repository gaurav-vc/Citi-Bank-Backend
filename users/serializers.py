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

        profile = getattr(obj, 'profile', None)
        dept = getattr(profile, 'department', None) if profile else None
        site = getattr(profile, 'site', None) if profile else None

        dept_perms = {}
        if dept:
            dept_mapping = RoleAccessMapping.objects.filter(
                role__role_name__iexact=obj.role, department=dept
            ).order_by('-id').first()
            if dept_mapping:
                dept_perms = dict(dept_mapping.permissions or {})

        global_perms = {}
        global_mapping = RoleAccessMapping.objects.filter(
            role__role_name__iexact=obj.role, department=None
        ).order_by('-id').first()
        
        # Fallback for CXO exact string mismatch (e.g. user has cxo_emb, role is CXO EMB)
        if not global_mapping and 'cxo' in (obj.role or '').lower():
            global_mapping = RoleAccessMapping.objects.filter(
                role__role_name__icontains='cxo', department=None
            ).exclude(permissions={}).order_by('-id').first()

        if global_mapping:
            global_perms = dict(global_mapping.permissions or {})

        # Merge both permission dictionaries using a logical OR
        all_keys = set(dept_perms.keys()).union(set(global_perms.keys()))
        for key in all_keys:
            d_perms = dept_perms.get(key, {})
            g_perms = global_perms.get(key, {})
            
            merged = {}
            action_keys = set(d_perms.keys()).union(set(g_perms.keys()))
            for act in action_keys:
                merged[act] = bool(d_perms.get(act, False) or g_perms.get(act, False))
                
            role_permissions[key] = merged

        # 2. Always ensure core:dashboard is present so user can see the dashboard
        dashboard_perm = {'view': True, 'create': False, 'edit': False, 'modify': False, 'cancel': False, 'delete': False}
        role_permissions.setdefault('core:dashboard', dashboard_perm)

        # 3. If user is super_admin — return all permissions without filtering
        if obj.role == 'super_admin':
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
                role_permissions = filtered

        # --- DEBUG DUMP ---
        try:
            import json
            import os
            debug_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug_perms.txt')
            with open(debug_path, 'w') as f:
                f.write(f"Role: {obj.role}\n")
                if site and site.module_configuration:
                    f.write(f"Site CFG: {json.dumps(site.module_configuration)}\n")
                f.write(f"Final Perms: {json.dumps(role_permissions, indent=2)}\n")
        except Exception:
            pass
        # ------------------

        return role_permissions
