from django.contrib import admin
from .models import Role, RoleModulePermission


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        'role_name',
        'role_code',
        'organization',
        'site',
        'access_level',
        'approval_limit',
        'status',
        'is_system_role',
        'created_at',
    )
    list_filter = ('status', 'access_level', 'is_system_role', 'dashboard_type')
    search_fields = ('role_name', 'role_code', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RoleModulePermission)
class RoleModulePermissionAdmin(admin.ModelAdmin):
    list_display = (
        'role',
        'module_key',
        'can_view',
        'can_create',
        'can_edit',
        'can_delete',
        'can_approve',
    )
    list_filter = ('module_key', 'can_view', 'can_create', 'can_edit', 'can_delete', 'can_approve')
    search_fields = ('role__role_name', 'module_key')
