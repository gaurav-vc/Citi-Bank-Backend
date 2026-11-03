from django.contrib import admin
from .models import AppModule, AppFeature, RoleAccessMapping, InventoryMasterField


@admin.register(AppModule)
class AppModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'module_order')
    ordering = ('module_order',)
    search_fields = ('name',)


@admin.register(AppFeature)
class AppFeatureAdmin(admin.ModelAdmin):
    list_display = ('feature_key', 'label', 'module')
    list_filter = ('module',)
    search_fields = ('feature_key', 'label')


@admin.register(RoleAccessMapping)
class RoleAccessMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'department')
    list_filter = ('role', 'department')
    search_fields = ('role', 'department')


@admin.register(InventoryMasterField)
class InventoryMasterFieldAdmin(admin.ModelAdmin):
    list_display = ('field_type', 'value', 'label', 'is_mandatory', 'is_active')
    list_filter = ('field_type', 'is_mandatory', 'is_active')
    search_fields = ('value', 'label', 'description')
