from django.contrib import admin
from .models import (
    Organization,
    Site,
    Department,
    SiteModuleAccess,
    SubscriptionInvoice,
    SystemOption,
    BillingFAQ,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'organization_type',
        'status',
        'is_active',
        'contact_email',
        'contact_phone',
        'created_at',
    )
    list_filter = ('status', 'organization_type', 'is_active')
    search_fields = ('name', 'code', 'legal_name', 'gst_number', 'pan_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'organization',
        'site_type',
        'site_manager_name',
        'site_manager_email',
        'is_active',
        'created_at',
    )
    list_filter = ('site_type', 'is_active', 'organization')
    search_fields = ('name', 'code', 'site_manager_name', 'site_manager_email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'site',
        'department_head',
        'budget_limit',
        'approval_limit',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active', 'site')
    search_fields = ('name', 'code', 'department_head')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SiteModuleAccess)
class SiteModuleAccessAdmin(admin.ModelAdmin):
    list_display = ('site', 'module_key', 'is_enabled')
    list_filter = ('module_key', 'is_enabled', 'site')
    search_fields = ('site__name', 'module_key')


@admin.register(SubscriptionInvoice)
class SubscriptionInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'organization', 'amount', 'billing_date', 'due_date', 'status', 'created_at')
    list_filter = ('status', 'organization')
    search_fields = ('invoice_number', 'organization__name')
    readonly_fields = ('created_at',)


@admin.register(SystemOption)
class SystemOptionAdmin(admin.ModelAdmin):
    list_display = ('category', 'value', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('category', 'value')
    readonly_fields = ('created_at',)


@admin.register(BillingFAQ)
class BillingFAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer')
    readonly_fields = ('created_at',)
