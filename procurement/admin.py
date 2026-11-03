from django.contrib import admin
from .models import (
    Indent,
    PurchaseOrder,
    Invoice,
    RFQ,
    Budget,
    Expense,
    PaymentProposal,
    Quotation,
    BidLog,
    ItemCategory,
    BudgetRevisionLog,
)


@admin.register(Indent)
class IndentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'type',
        'category',
        'status',
        'approval_level',
        'current_approver',
        'estimated_cost',
        'priority',
        'created_at',
    )
    list_filter = ('status', 'approval_level', 'category', 'requisition_type', 'priority')
    search_fields = ('id', 'category', 'justification', 'current_approver', 'created_by')
    readonly_fields = ('created_at',)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'type',
        'vendor_name',
        'status',
        'approval_level',
        'current_approver',
        'total_value',
        'net_value',
        'created_at',
    )
    list_filter = ('status', 'approval_level', 'category')
    search_fields = ('id', 'vendor_name', 'linked_rfq', 'current_approver', 'created_by')
    readonly_fields = ('created_at',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number',
        'vendor_name',
        'po_id',
        'total_amount',
        'status',
        'approval_level',
        'current_approver',
        'matching_status',
        'due_date',
        'created_at',
    )
    list_filter = ('status', 'matching_status', 'approval_level')
    search_fields = ('invoice_number', 'vendor_name', 'po_id', 'grn_id', 'created_by')
    readonly_fields = ('created_at',)


@admin.register(RFQ)
class RFQAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'category',
        'bidding_type',
        'status',
        'approval_level',
        'estimated_value',
        'bid_due_date',
        'created_at',
    )
    list_filter = ('status', 'bidding_type', 'category')
    search_fields = ('id', 'title', 'category', 'linked_pr', 'created_by')
    readonly_fields = ('created_at',)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fy',
        'type',
        'department',
        'category',
        'gl_code',
        'annual_budget',
        'allocated',
        'committed',
        'actual',
        'status',
        'created_at',
    )
    list_filter = ('status', 'fy', 'type', 'department')
    search_fields = ('id', 'gl_code', 'department', 'owner')
    readonly_fields = ('created_at',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'category',
        'amount',
        'date',
        'payment_mode',
        'status',
        'current_approver',
        'vendor',
        'created_at',
    )
    list_filter = ('status', 'payment_mode', 'category')
    search_fields = ('id', 'description', 'po_id', 'invoice_id', 'vendor')
    readonly_fields = ('created_at',)


@admin.register(PaymentProposal)
class PaymentProposalAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'vendor_name',
        'total_amount',
        'net_payable',
        'status',
        'approval_level',
        'current_approver',
        'due_date',
        'created_at',
    )
    list_filter = ('status', 'approval_level')
    search_fields = ('id', 'vendor_name', 'vendor_id', 'utr_number')
    readonly_fields = ('created_at',)


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'rfq_id',
        'vendor_name',
        'total_cost',
        'compliance_status',
        'status',
        'created_at',
    )
    list_filter = ('status', 'compliance_status')
    search_fields = ('id', 'rfq_id', 'vendor_name')
    readonly_fields = ('created_at',)


@admin.register(BidLog)
class BidLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'rfq_id',
        'vendor_name',
        'bid_amount',
        'status',
        'timestamp',
    )
    list_filter = ('status',)
    search_fields = ('rfq_id', 'vendor_name')
    readonly_fields = ('timestamp',)


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BudgetRevisionLog)
class BudgetRevisionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'budget', 'previous_allocation', 'new_allocation', 'updated_by', 'created_at')
    search_fields = ('budget__gl_code', 'updated_by', 'remarks')
    readonly_fields = ('created_at',)
