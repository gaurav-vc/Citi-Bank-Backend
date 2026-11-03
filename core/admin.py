from django.contrib import admin
from .models import DocumentationItem, Notification


@admin.register(DocumentationItem)
class DocumentationItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'user__email')
    readonly_fields = ('created_at',)
