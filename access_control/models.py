from django.db import models

class Role(models.Model):
    role_name = models.CharField(max_length=100)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, null=True, blank=True, db_column='organization_id')
    site = models.ForeignKey('organizations.Site', on_delete=models.CASCADE, null=True, blank=True, db_column='site_id')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    # Enriched fields
    access_level = models.CharField(max_length=50, default='Department')
    approval_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    role_code = models.CharField(max_length=50, default='')
    dashboard_type = models.CharField(max_length=100, default='Default')
    cross_dept_access = models.BooleanField(default=False)

    # Permission booleans
    can_create_po = models.BooleanField(default=False)
    can_approve_po = models.BooleanField(default=False)
    can_manage_vendors = models.BooleanField(default=False)
    can_manage_inventory = models.BooleanField(default=False)
    can_manage_payments = models.BooleanField(default=False)
    can_manage_contracts = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_manage_roles = models.BooleanField(default=False)
    can_export_reports = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)

    is_system_role = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        unique_together = ('role_name', 'organization', 'site')

class RoleModulePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='module_permissions')
    module_key = models.CharField(max_length=100)
    
    can_view = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)

    class Meta:
        db_table = 'role_module_permissions'
        unique_together = ('role', 'module_key')


def sync_role_access_mapping(role):
    from setups.models import RoleAccessMapping
    permissions_list = RoleModulePermission.objects.filter(role=role)
    perms = {}
    for rp in permissions_list:
        perms[rp.module_key] = {
            'view': rp.can_view,
            'create': rp.can_create,
            'edit': rp.can_edit,
            'delete': rp.can_delete,
            'approve': rp.can_approve
        }
    
    mappings = RoleAccessMapping.objects.filter(role=role, department__isnull=True)
    if mappings.exists():
        mapping = mappings.first()
        mapping.permissions = perms
        mapping.save()
        if mappings.count() > 1:
            mappings.exclude(id=mapping.id).delete()
    else:
        RoleAccessMapping.objects.create(role=role, department=None, permissions=perms)

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=RoleModulePermission)
def role_module_permission_saved(sender, instance, **kwargs):
    sync_role_access_mapping(instance.role)

@receiver(post_delete, sender=RoleModulePermission)
def role_module_permission_deleted(sender, instance, **kwargs):
    sync_role_access_mapping(instance.role)

