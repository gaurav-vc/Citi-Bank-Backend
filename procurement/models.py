from django.db import models
from django.conf import settings
from workflows.models import WorkflowAbstractModel

class Indent(WorkflowAbstractModel):
    id = models.CharField(max_length=50, primary_key=True)
    type = models.CharField(max_length=50) # 'material', 'service', 'amc'
    tower = models.CharField(max_length=50)
    floor = models.CharField(max_length=50)
    category = models.CharField(max_length=100)
    items = models.JSONField(default=list)
    estimated_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    required_date = models.DateField()
    budget_head = models.CharField(max_length=50)
    justification = models.TextField(blank=True, null=True)
    attachments = models.JSONField(default=list)
    approvals = models.JSONField(default=list)
    requisition_type = models.CharField(max_length=50, default='regular') # 'regular', 'emergency', 'maintenance', 'asset', 'capex'
    priority = models.CharField(max_length=50, default='medium') # 'low', 'medium', 'high', 'critical'
    inventory_status = models.CharField(max_length=50, default='pending') # 'pending', 'fully_available', 'partially_available', 'not_available'
    inventory_recommendation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'indents'

class PurchaseOrder(WorkflowAbstractModel):
    id = models.CharField(max_length=50, primary_key=True)
    type = models.CharField(max_length=50) # 'po', 'wo', 'amc'
    vendor = models.CharField(max_length=50)
    vendor_name = models.CharField(max_length=255)
    linked_rfq = models.CharField(max_length=50, blank=True, null=True)
    items = models.JSONField(default=list)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    taxes = models.DecimalField(max_digits=15, decimal_places=2)
    net_value = models.DecimalField(max_digits=15, decimal_places=2)
    retention_percent = models.IntegerField(default=0)
    milestones = models.JSONField(default=list)
    start_date = models.DateField()
    end_date = models.DateField()
    tower = models.CharField(max_length=50)
    category = models.CharField(max_length=100)
    attachments = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'purchase_orders'

class Invoice(WorkflowAbstractModel):
    id = models.CharField(max_length=50, primary_key=True)
    vendor_id = models.CharField(max_length=50)
    vendor_name = models.CharField(max_length=255)
    invoice_number = models.CharField(max_length=100)
    invoice_date = models.DateField()
    po_id = models.CharField(max_length=50)
    grn_id = models.CharField(max_length=50, blank=True, null=True)
    ses_id = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    gst = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    due_date = models.DateField()
    matching_status = models.CharField(max_length=50, default='2way')
    attachments = models.JSONField(default=list)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invoices'

class RFQ(WorkflowAbstractModel):
    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    tower = models.CharField(max_length=50)
    linked_pr = models.CharField(max_length=50, blank=True, null=True)
    estimated_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    bid_due_date = models.DateField()
    vendors = models.JSONField(default=list)
    created_date = models.DateField()
    recommended_quotation_id = models.CharField(max_length=50, blank=True, null=True)
    recommended_vendor_id = models.CharField(max_length=50, blank=True, null=True)
    recommendation_comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rfqs'

class Budget(WorkflowAbstractModel):
    id = models.CharField(max_length=50, primary_key=True)
    fy = models.CharField(max_length=50)
    type = models.CharField(max_length=50) # 'opex', 'capex'
    tower = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    gl_code = models.CharField(max_length=100)
    period = models.CharField(max_length=50)
    annual_budget = models.DecimalField(max_digits=15, decimal_places=2)
    allocated = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    committed = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    actual = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    owner = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'budgets'

class Expense(WorkflowAbstractModel):
    id = models.CharField(max_length=50, primary_key=True)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    date = models.DateField()
    payment_mode = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    po_id = models.CharField(max_length=50, blank=True, null=True)
    invoice_id = models.CharField(max_length=50, blank=True, null=True)
    payment_proposal_id = models.CharField(max_length=50, blank=True, null=True)
    vendor = models.CharField(max_length=255, blank=True, null=True)
    tower = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, default='paid')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'expenses'

class PaymentProposal(WorkflowAbstractModel):
    id = models.CharField(max_length=50, primary_key=True)
    vendor_name = models.CharField(max_length=255)
    vendor_id = models.CharField(max_length=50)
    invoices = models.JSONField(default=list)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    gst_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    retention_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    net_payable = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    due_date = models.DateField()
    created_date = models.DateField()
    max_approval_level = models.IntegerField(default=1)
    utr_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_proposals'


class Quotation(WorkflowAbstractModel):
    id = models.CharField(max_length=50, primary_key=True)
    rfq_id = models.CharField(max_length=50)
    vendor_id = models.CharField(max_length=50)
    vendor_name = models.CharField(max_length=255)
    base_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    tax_breakdown = models.JSONField(default=dict)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    delivery_timeline = models.CharField(max_length=100)
    warranty = models.CharField(max_length=100, blank=True, null=True)
    vendor_rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    remarks = models.TextField(blank=True, null=True)
    terms_conditions = models.TextField(blank=True, null=True)
    attachments = models.JSONField(default=list)
    technical_score = models.IntegerField(default=80)
    commercial_score = models.IntegerField(default=80)
    overall_score = models.IntegerField(default=80)
    compliance_status = models.CharField(max_length=50, default='Compliant')
    pros = models.JSONField(default=list, blank=True)
    cons = models.JSONField(default=list, blank=True)
    risks = models.JSONField(default=list, blank=True)
    commercial_advantages = models.JSONField(default=list, blank=True)
    technical_advantages = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quotations'


class ItemCategory(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'item_categories'

    def __str__(self):
        return f"{self.name} ({self.code})"


class BudgetRevisionLog(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='revision_logs')
    previous_allocation = models.DecimalField(max_digits=15, decimal_places=2)
    new_allocation = models.DecimalField(max_digits=15, decimal_places=2)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'budget_revision_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Revision for {self.budget_id} ({self.previous_allocation} -> {self.new_allocation})"

