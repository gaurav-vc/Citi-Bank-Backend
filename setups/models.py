from django.db import models
from access_control.models import Role
from organizations.models import Department

class AppModule(models.Model):
    name = models.CharField(max_length=100)
    module_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'app_modules'

class AppFeature(models.Model):
    module = models.ForeignKey(AppModule, on_delete=models.CASCADE, db_column='module_id')
    feature_key = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=100)

    class Meta:
        db_table = 'app_features'

class RoleAccessMapping(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='role_id')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='department_id', null=True, blank=True)
    permissions = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'role_access_mappings'
        unique_together = ('role', 'department')

class InventoryMasterField(models.Model):
    field_type = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True, help_text="Advanced description or instructions for this field")
    is_mandatory = models.BooleanField(default=False, help_text="Toggle if this option requires strict compliance")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'inventory_master_fields'
        unique_together = ('field_type', 'value')
