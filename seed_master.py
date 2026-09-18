import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from setups.models import InventoryMasterField

def seed_data():
    defaults = [
        # Categories
        {'field_type': 'category', 'label': 'Electrical', 'value': 'electrical'},
        {'field_type': 'category', 'label': 'HVAC', 'value': 'hvac'},
        {'field_type': 'category', 'label': 'Plumbing', 'value': 'plumbing'},
        {'field_type': 'category', 'label': 'Housekeeping', 'value': 'housekeeping'},
        {'field_type': 'category', 'label': 'Security', 'value': 'security'},
        
        # Towers
        {'field_type': 'tower', 'label': 'Tower A', 'value': 'tower_a'},
        {'field_type': 'tower', 'label': 'Tower B', 'value': 'tower_b'},
        
        # Request Types
        {'field_type': 'request_type', 'label': 'Material Request', 'value': 'material'},
        {'field_type': 'request_type', 'label': 'Service Request', 'value': 'service'},
        {'field_type': 'request_type', 'label': 'AMC Request', 'value': 'amc'},
        
        # Budget Heads
        {'field_type': 'budget_head', 'label': 'OPEX (Operational)', 'value': 'opex'},
        {'field_type': 'budget_head', 'label': 'CAPEX (Capital)', 'value': 'capex'},
    ]

    # Floors
    for i in range(1, 12):
        suffix = 'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'
        defaults.append({
            'field_type': 'floor',
            'label': f'{i}{suffix} Floor',
            'value': f'{i}f'
        })

    created_count = 0
    for item in defaults:
        obj, created = InventoryMasterField.objects.get_or_create(
            field_type=item['field_type'],
            value=item['value'],
            defaults={'label': item['label'], 'is_active': True}
        )
        if created:
            created_count += 1

    print(f"Successfully seeded {created_count} default options into the database!")

if __name__ == '__main__':
    seed_data()
