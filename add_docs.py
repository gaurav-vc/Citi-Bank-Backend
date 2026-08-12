import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from core.models import DocumentationItem

items = [
    {"title": "Dashboard", "category": "module_guide", "order": 1},
    {"title": "Procurement", "category": "module_guide", "order": 2},
    {"title": "Inventory", "category": "module_guide", "order": 3},
    {"title": "QC & Execution", "category": "module_guide", "order": 4},
    {"title": "Finance & Billing", "category": "module_guide", "order": 5},
]

for item in items:
    DocumentationItem.objects.update_or_create(
        title=item["title"],
        category=item["category"],
        defaults={"order": item["order"], "is_active": True}
    )

print("Successfully added the 5 documentation items!")
