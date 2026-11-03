from django.contrib import admin
from .models import Vendor, RateContract, AuditLog


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'type',
        'category',
        'contact_person',
        'email',
        'phone',
        'status',
        'onboarding_status',
        'is_universal_vendor',
        'created_at',
    )
    list_filter = ('type', 'status', 'onboarding_status', 'is_universal_vendor')
    search_fields = ('name', 'email', 'phone', 'gst_number', 'pan')
    readonly_fields = ('created_at',)


@admin.register(RateContract)
class RateContractAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'vendor',
        'type',
        'contract_value',
        'billing_cycle',
        'start_date',
        'end_date',
        'status',
        'utilization_percent',
        'created_at',
    )
    list_filter = ('type', 'status', 'billing_cycle')
    search_fields = ('vendor__name', 'service_scope')
    readonly_fields = ('created_at',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'target_type', 'target_id', 'actioned_by', 'timestamp')
    list_filter = ('action', 'target_type')
    search_fields = ('target_id', 'actioned_by', 'comments')
    readonly_fields = ('timestamp',)
