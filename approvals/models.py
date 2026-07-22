from django.db import models
from django.conf import settings

class ApprovalRequest(models.Model):
    ENTITY_TYPES = [
        ('indent', 'Indent'),
        ('purchase_order', 'Purchase Order'),
        ('grn', 'GRN'),
        ('invoice', 'Invoice'),
        ('expense', 'Expense'),
        ('payment', 'Payment'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPES)
    entity_id = models.CharField(max_length=50)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='approval_requests')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_approvals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'approval_requests'
