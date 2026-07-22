import os
import sys
import django
import uuid

# Add the backend directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from inventory.models import Item

DUMMY_ITEMS = [
    {"name": "Electrical Wires (1mm)", "category": "Electrical", "uom": "Roll", "unit_price": 1200, "type": "spare"},
    {"name": "LED Bulbs 15W", "category": "Electrical", "uom": "Nos", "unit_price": 150, "type": "spare"},
    {"name": "AC Filter", "category": "HVAC", "uom": "Nos", "unit_price": 450, "type": "spare"},
    {"name": "PVC Pipe 1 inch", "category": "Plumbing", "uom": "Meter", "unit_price": 85, "type": "spare"},
    {"name": "Cleaning Liquid", "category": "Housekeeping", "uom": "Liter", "unit_price": 250, "type": "consumable"},
    {"name": "Security Badge", "category": "Security", "uom": "Nos", "unit_price": 50, "type": "consumable"},
]

def seed():
    count = 0
    for data in DUMMY_ITEMS:
        item_id = f"ITM-{uuid.uuid4().hex[:6].upper()}"
        obj, created = Item.objects.get_or_create(
            name=data["name"],
            defaults={
                "id": item_id,
                "category": data["category"],
                "uom": data["uom"],
                "unit_price": data["unit_price"],
                "type": data["type"],
                "min_stock_level": 10,
                "current_stock": 50,
            }
        )
        if created:
            count += 1
    
    print(f"✅ Successfully seeded {count} items into the database!")

if __name__ == "__main__":
    seed()
