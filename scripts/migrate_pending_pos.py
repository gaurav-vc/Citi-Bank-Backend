"""
Migration script to transition all Purchase Orders in status 'pending_procurement_approval' to 'approved'.
Run from backend directory: python scripts/migrate_pending_pos.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from procurement.models import PurchaseOrder

def migrate_pos():
    pending_pos = PurchaseOrder.objects.filter(status='pending_procurement_approval')
    count = pending_pos.count()
    print(f"Found {count} POs in 'pending_procurement_approval' status.")
    
    if count > 0:
        updated = pending_pos.update(status='approved')
        print(f"Successfully migrated {updated} POs to 'approved' status.")
    else:
        print("No POs required migration.")

if __name__ == '__main__':
    migrate_pos()
