from django.core.management.base import BaseCommand
from procurement.models import ItemCategory

class Command(BaseCommand):
    help = 'Seeds the ItemCategory table with default categories'

    def handle(self, *args, **options):
        default_categories = [
            {'code': 'ELEC', 'name': 'Electrical', 'description': 'Electrical supplies, works, and maintenance'},
            {'code': 'HVAC', 'name': 'HVAC', 'description': 'Heating, ventilation, and air conditioning'},
            {'code': 'PLMB', 'name': 'Plumbing', 'description': 'Plumbing installations and repairs'},
            {'code': 'HKP', 'name': 'Housekeeping', 'description': 'Cleaning and housekeeping services/consumables'},
            {'code': 'SEC', 'name': 'Security', 'description': 'Security apparatus and services'},
            {'code': 'LAND', 'name': 'Landscaping', 'description': 'Horticulture, gardening, and landscaping'},
            {'code': 'MEP', 'name': 'MEP Spares', 'description': 'Mechanical, electrical, and plumbing spare parts'},
            {'code': 'SAFE', 'name': 'Safety', 'description': 'Safety gear, signs, and compliance elements'},
        ]

        for cat in default_categories:
            category, created = ItemCategory.objects.get_or_create(
                name=cat['name'],
                defaults={
                    'code': cat['code'],
                    'description': cat['description'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {category.name} ({category.code})"))
            else:
                # Ensure code is updated if name matches but code was different
                category.code = cat['code']
                category.is_active = True
                category.save()
                self.stdout.write(self.style.SUCCESS(f"Category already exists: {category.name} ({category.code})"))

        self.stdout.write(self.style.SUCCESS("Item categories seeding completed successfully."))
