import os
import sys
import django

sys.path.append(r"c:\Users\MC VIP\OneDrive\Desktop\CitiBank\Campusspend\backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campusspend.settings")
django.setup()

from vendors.models import Vendor
from procurement.models import PurchaseOrder, Invoice, Indent

print(f"Total Vendors: {Vendor.objects.count()}")
print(f"Total POs: {PurchaseOrder.objects.count()}")
print(f"Total Invoices: {Invoice.objects.count()}")
print(f"Total Indents: {Indent.objects.count()}")

for v in Vendor.objects.all()[:3]:
    print(f"Vendor: {v.name} (Code: {v.code})")

for p in PurchaseOrder.objects.all()[:3]:
    print(f"PO: {p.po_number} (Vendor: {p.vendor_name})")
