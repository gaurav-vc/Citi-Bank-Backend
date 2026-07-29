from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=50, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    # Enriched fields
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    entity_name = models.CharField(max_length=255, blank=True, null=True)
    organization_type = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    pan_number = models.CharField(max_length=50, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zone = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    currency = models.CharField(max_length=10, default='INR')
    timezone = models.CharField(max_length=50, default='UTC')
    billing_type = models.CharField(max_length=50, blank=True, null=True)
    billing_cycle = models.CharField(max_length=50, blank=True, null=True)
    billing_term = models.CharField(max_length=50, blank=True, null=True)
    billing_rate = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    billing_start_date = models.DateField(blank=True, null=True)
    billing_end_date = models.DateField(blank=True, null=True)
    billing_date = models.DateField(blank=True, null=True)
    project_duration = models.IntegerField(default=0)
    white_label = models.BooleanField(default=False)
    sub_domain = models.CharField(max_length=255, blank=True, null=True)
    approval_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    logo = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations'

class Site(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, db_column='organization_id')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Enriched fields
    site_type = models.CharField(max_length=100, blank=True, null=True)
    site_head = models.CharField(max_length=255, blank=True, null=True)
    site_manager_name = models.CharField(max_length=255, blank=True, null=True)
    site_manager_email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    storage_capacity = models.CharField(max_length=100, blank=True, null=True)
    budget_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    active_projects = models.IntegerField(default=0)
    module_configuration = models.JSONField(default=dict, blank=True)
    feature_flags = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sites'

class Department(models.Model):
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, db_column='site_id')
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Enriched fields
    code = models.CharField(max_length=50, blank=True, null=True)
    department_head = models.CharField(max_length=255, blank=True, null=True)
    cost_center_code = models.CharField(max_length=50, blank=True, null=True)
    budget_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    approval_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'

class SiteModuleAccess(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='module_access')
    module_key = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        db_table = 'site_module_access'
        unique_together = ('site', 'module_key')

class SubscriptionInvoice(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='subscription_invoices')
    invoice_number = models.CharField(max_length=100, unique=True)
    billing_date = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending') # Paid, Overdue, Pending
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subscription_invoices'

class SystemOption(models.Model):
    category = models.CharField(max_length=100) # e.g. 'solution_type', 'industry', 'billing_term', 'billing_cycle'
    value = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'system_options'
        unique_together = ('category', 'value')

class BillingFAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'billing_faqs'
        ordering = ['order']
