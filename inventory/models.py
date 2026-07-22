from django.db import models

class Item(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50) # 'spare', 'consumable', 'service'
    category = models.CharField(max_length=100)
    uom = models.CharField(max_length=50)
    min_stock_level = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=0)
    current_stock = models.IntegerField(default=0)
    preferred_vendor = models.CharField(max_length=50, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'items'

class GRN(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    po_id = models.CharField(max_length=50) # references purchase_orders.id
    received_date = models.DateField()
    received_by = models.CharField(max_length=100)
    items = models.JSONField(default=list)
    status = models.CharField(max_length=50, default='pending')
    invoice_status = models.CharField(max_length=50, default='pending')
    vendor_name = models.CharField(max_length=255, blank=True, default='')
    invoice_number = models.CharField(max_length=100, blank=True, default='')
    remarks = models.TextField(blank=True, default='')
    inspected_by = models.CharField(max_length=100, blank=True, null=True)
    inspected_at = models.DateTimeField(blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    attachments = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'grns'

class ProductInspection(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    po_id = models.CharField(max_length=50) # references purchase_orders.id
    vendor_name = models.CharField(max_length=255, blank=True, default='')
    received_date = models.DateField()
    inspector_name = models.CharField(max_length=100)
    items = models.JSONField(default=list)
    status = models.CharField(max_length=50, default='pending') # pending, completed, rejected
    challan_number = models.CharField(max_length=100, blank=True, default='')
    invoice_number = models.CharField(max_length=100, blank=True, default='')
    invoice_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, default='')
    attachments = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_inspections'

class StockTransfer(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    items = models.JSONField(default=list)
    requested_by = models.CharField(max_length=100)
    requested_date = models.DateField()
    status = models.CharField(max_length=50, default='pending')
    approved_by = models.CharField(max_length=100, blank=True, null=True)
    transfer_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stock_transfers'

class MaterialIssue(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    items = models.JSONField(default=list)
    issued_to = models.CharField(max_length=100)
    issued_date = models.DateField()
    tower = models.CharField(max_length=50)
    floor = models.CharField(max_length=50)
    purpose = models.TextField()
    status = models.CharField(max_length=50, default='issued')
    department = models.CharField(max_length=100, blank=True, null=True)
    work_order_ref = models.CharField(max_length=50, blank=True, null=True)
    issued_by = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'material_issues'

class ScrapDisposal(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    items = models.JSONField(default=list)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    disposal_date = models.DateField()
    buyer = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='pending')
    gate_pass_no = models.CharField(max_length=50, blank=True, null=True)
    recovered_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scrap_disposals'

class GoodsDispatchNote(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    grn_id = models.CharField(max_length=50)
    destination = models.CharField(max_length=255)
    items = models.JSONField(default=list)
    status = models.CharField(max_length=50, default='dispatched')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'goods_dispatch_notes'

class ReturnToVendor(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    grn_id = models.CharField(max_length=50)
    vendor_reference = models.CharField(max_length=255)
    items = models.JSONField(default=list)
    reason = models.TextField(blank=True, default='')
    status = models.CharField(max_length=50, default='returned')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'returns_to_vendor'

class StockLedger(models.Model):
    TRANSACTION_TYPES = [
        ('GRN_RECEIPT', 'GRN Receipt'),
        ('MANUAL_ADJUSTMENT', 'Manual Adjustment'),
        ('RETURN_FROM_SITE', 'Return From Site'),
        ('GOODS_ISSUE', 'Goods Issue'),
        ('RETURN_TO_VENDOR', 'Return To Vendor'),
        ('OPENING_BALANCE', 'Opening Balance'),
    ]
    SOURCE_TYPES = [
        ('GRN', 'Goods Receipt Note'),
        ('GDN', 'Goods Dispatch Note'),
        ('RTV', 'Return To Vendor'),
        ('MANUAL', 'Manual Entry'),
        ('SYSTEM', 'System Entry'),
    ]
    id = models.CharField(max_length=50, primary_key=True)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES, blank=True, null=True)
    source_id = models.CharField(max_length=50, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    stock_before = models.IntegerField()
    stock_after = models.IntegerField()
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    reference_number = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stock_ledger'
        ordering = ['-timestamp']