from django.db import models
from django.conf import settings

class WorkflowAbstractModel(models.Model):
    status = models.CharField(max_length=50, default='draft')
    current_approver = models.CharField(max_length=255, blank=True, null=True)
    next_role = models.CharField(max_length=100, blank=True, null=True)
    workflow_history = models.JSONField(default=list, blank=True)
    approval_level = models.IntegerField(default=0)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    approved_by = models.CharField(max_length=255, blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    rejected_by = models.CharField(max_length=255, blank=True, null=True)
    rejected_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class WorkflowRule(models.Model):
    module = models.CharField(max_length=100) # 'indents', 'payments'
    min_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2, default=999999999.99)
    department_id = models.IntegerField(blank=True, null=True)
    required_role_name = models.CharField(max_length=100)
    step_sequence = models.IntegerField(default=1)
    sla_hours = models.IntegerField(default=24)
    conditional_type = models.CharField(max_length=100, default='always') # 'always', 'capex_only', 'opex_only'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workflow_rules'

class WorkflowInstance(models.Model):
    module = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_instances'
        unique_together = ('module', 'entity_id')

class WorkflowStep(models.Model):
    instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, db_column='instance_id')
    step_sequence = models.IntegerField()
    assigned_role_name = models.CharField(max_length=100)
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='assigned_user_id', related_name='assigned_steps')
    status = models.CharField(max_length=50, default='pending') # 'pending', 'approved', 'rejected', 'escalated'
    sla_hours = models.IntegerField(default=24)
    due_at = models.DateTimeField()
    actioned_at = models.DateTimeField(null=True, blank=True)
    actioned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='actioned_by', related_name='actioned_steps')
    comments = models.TextField(blank=True, null=True)
    escalated_to_role = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'workflow_steps'
