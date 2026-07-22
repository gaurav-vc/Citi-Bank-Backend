from django.db import models

class Vendor(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50) # 'material', 'service', 'amc', 'soft_services'
    category = models.CharField(max_length=100)
    gst_number = models.CharField(max_length=50)
    pan = models.CharField(max_length=50)
    msme_status = models.BooleanField(default=False)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)
    ifsc = models.CharField(max_length=50)
    sla_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    approved_towers = models.JSONField(default=list) # e.g. ["Tower A", "Tower B"]
    compliance_expiry = models.DateField()
    status = models.CharField(max_length=50, default='active')
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    user_id = models.CharField(max_length=100, blank=True, null=True)
    onboarding_status = models.CharField(max_length=50, default='Account Created')
    is_universal_vendor = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vendors'

class RateContract(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    vendor = models.CharField(max_length=255)
    vendor_id = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    service_scope = models.TextField()
    category = models.CharField(max_length=100)
    contract_value = models.DecimalField(max_digits=15, decimal_places=2)
    billing_cycle = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    sla_kpis = models.JSONField(default=list)
    status = models.CharField(max_length=50, default='active')
    utilization_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    last_billing_date = models.DateField(null=True, blank=True)
    next_billing_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rate_contracts'

class AuditLog(models.Model):
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50)
    target_id = models.CharField(max_length=100)
    actioned_by = models.CharField(max_length=100)
    comments = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vendor_audit_logs'
