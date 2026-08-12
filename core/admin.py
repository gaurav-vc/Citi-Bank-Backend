from django.contrib import admin
from .models import DocumentationItem

@admin.register(DocumentationItem)
class DocumentationItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description')

