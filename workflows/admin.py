from django.contrib import admin
from .models import WorkflowRule, WorkflowInstance, WorkflowStep


@admin.register(WorkflowRule)
class WorkflowRuleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'module',
        'step_sequence',
        'required_role_name',
        'min_amount',
        'max_amount',
        'department_id',
        'sla_hours',
        'conditional_type',
        'created_at',
    )
    list_filter = ('module', 'required_role_name', 'conditional_type')
    search_fields = ('module', 'required_role_name', 'department_id')
    readonly_fields = ('created_at',)


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'module', 'entity_id', 'status', 'created_at', 'updated_at')
    list_filter = ('module', 'status')
    search_fields = ('entity_id', 'module')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'instance',
        'step_sequence',
        'assigned_role_name',
        'assigned_user',
        'status',
        'sla_hours',
        'due_at',
        'actioned_at',
        'actioned_by',
    )
    list_filter = ('status', 'assigned_role_name')
    search_fields = ('assigned_role_name', 'assigned_user', 'comments')
    readonly_fields = ('actioned_at',)
