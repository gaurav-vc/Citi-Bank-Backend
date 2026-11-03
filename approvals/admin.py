from django.contrib import admin
from .models import ApprovalRequest


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'entity_type',
        'entity_id',
        'requested_by',
        'assigned_to',
        'status',
        'created_at',
        'updated_at',
    )
    list_filter = ('entity_type', 'status')
    search_fields = ('entity_id', 'requested_by', 'assigned_to', 'remarks')
    readonly_fields = ('created_at', 'updated_at')
