from django.contrib import admin
from .models import (
    Item,
    GRN,
    ProductInspection,
    StockTransfer,
    MaterialIssue,
    ScrapDisposal,
    GoodsDispatchNote,
    ReturnToVendor,
    StockLedger,
)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'type',
        'category',
        'current_stock',
        'uom',
        'unit_price',
        'min_stock_level',
        'reorder_level',
        'created_at',
    )
    list_filter = ('type', 'category')
    search_fields = ('name', 'category', 'preferred_vendor')
    readonly_fields = ('created_at',)


@admin.register(GRN)
class GRNAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'po_id',
        'vendor_name',
        'invoice_number',
        'received_date',
        'status',
        'invoice_status',
        'created_at',
    )
    list_filter = ('status', 'invoice_status')
    search_fields = ('po_id', 'vendor_name', 'invoice_number', 'inspected_by')
    readonly_fields = ('created_at',)


@admin.register(ProductInspection)
class ProductInspectionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'po_id',
        'vendor_name',
        'inspector_name',
        'received_date',
        'status',
        'challan_number',
        'created_at',
    )
    list_filter = ('status',)
    search_fields = ('po_id', 'vendor_name', 'inspector_name', 'challan_number')
    readonly_fields = ('created_at',)


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'from_location',
        'to_location',
        'requested_by',
        'requested_date',
        'status',
        'approved_by',
        'transfer_date',
        'created_at',
    )
    list_filter = ('status',)
    search_fields = ('from_location', 'to_location', 'requested_by')
    readonly_fields = ('created_at',)


@admin.register(MaterialIssue)
class MaterialIssueAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'issued_to',
        'issued_date',
        'tower',
        'floor',
        'department',
        'purpose',
        'status',
        'created_at',
    )
    list_filter = ('status', 'department', 'tower')
    search_fields = ('issued_to', 'purpose', 'work_order_ref', 'issued_by')
    readonly_fields = ('created_at',)


@admin.register(ScrapDisposal)
class ScrapDisposalAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'buyer',
        'total_value',
        'recovered_value',
        'disposal_date',
        'gate_pass_no',
        'status',
        'created_at',
    )
    list_filter = ('status',)
    search_fields = ('buyer', 'gate_pass_no')
    readonly_fields = ('created_at',)


@admin.register(GoodsDispatchNote)
class GoodsDispatchNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'grn_id', 'destination', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('grn_id', 'destination')
    readonly_fields = ('created_at',)


@admin.register(ReturnToVendor)
class ReturnToVendorAdmin(admin.ModelAdmin):
    list_display = ('id', 'grn_id', 'vendor_reference', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('grn_id', 'vendor_reference', 'reason')
    readonly_fields = ('created_at',)


@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'transaction_type',
        'source_type',
        'source_id',
        'item',
        'quantity',
        'stock_before',
        'stock_after',
        'timestamp',
    )
    list_filter = ('transaction_type', 'source_type')
    search_fields = ('source_id', 'reference_number', 'reason', 'remarks')
    readonly_fields = ('timestamp',)
