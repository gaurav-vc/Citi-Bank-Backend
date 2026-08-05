import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from approvals.models import ApprovalRequest
from utils.email_helper import send_workflow_approval_email
from procurement.models import Invoice

User = get_user_model()

def force_cxo_approval_and_email():
    # Find the CXO user
    cxo_user = User.objects.filter(role__in=['cxo_citi', 'cxo_emb'], is_active=True).first()
    if not cxo_user:
        print("No active CXO user found! Searching for any user with 'cxo' in role...")
        cxo_user = User.objects.filter(role__icontains='cxo', is_active=True).first()
        if not cxo_user:
            print("Still no CXO user found.")
            return

    print(f"Found CXO user: {cxo_user.email} (Role: {cxo_user.role})")

    # Get the specific pending approval request (ID: 4)
    try:
        approval = ApprovalRequest.objects.get(id=4, status='pending')
    except ApprovalRequest.DoesNotExist:
        print("Approval request ID 4 is not pending or does not exist.")
        return

    # Re-assign to CXO
    print(f"Re-assigning Approval ID {approval.id} from {approval.assigned_to.email} to {cxo_user.email}")
    approval.assigned_to = cxo_user
    approval.save()

    # Now trigger the email for this invoice
    entity_id = approval.entity_id
    try:
        invoice = Invoice.objects.get(id=entity_id)
    except Invoice.DoesNotExist:
        print(f"Invoice {entity_id} does not exist.")
        return

    title = "Invoice"
    real_module = "invoices"
    real_doc_id = str(invoice.id)
    
    # Amount
    v = getattr(invoice, 'net_value', None)
    if v is None: v = getattr(invoice, 'total_amount', None)
    if v is None: v = getattr(invoice, 'total_value', None)
    real_amount = float(v) if v is not None else 0.0

    # Vendor Name
    vendor_name = "N/A"
    if getattr(invoice, 'vendor', None):
        try:
            from vendors.models import Vendor
            v_obj = Vendor.objects.filter(id=invoice.vendor).first()
            if v_obj:
                vendor_name = getattr(v_obj, 'name', getattr(v_obj, 'company_name', 'Vendor'))
        except Exception:
            pass

    # Token
    from rest_framework_simplejwt.tokens import AccessToken
    from datetime import timedelta
    from django.conf import settings
    
    token = AccessToken()
    token["user_id"] = str(cxo_user.id)
    token["role"] = cxo_user.role
    token["approval_role"] = cxo_user.role
    token["module"] = real_module
    token["document_id"] = real_doc_id
    token["approval_link"] = True
    token["purpose"] = "email_approval"
    token.set_exp(lifetime=timedelta(seconds=getattr(settings, 'EMAIL_APPROVAL_TOKEN_LIFETIME_SECONDS', 3600)))
    
    portal_link = f"https://procurement.vibesandbox.live/billing/invoices/{real_doc_id}?token={str(token)}"

    # Send Email
    try:
        send_workflow_approval_email(
            user=cxo_user,
            module_name=real_module,
            document_id=real_doc_id,
            title=title,
            portal_link=portal_link,
            created_by="system.admin@example.com",
            vendor_name=vendor_name,
            amount=real_amount,
            stage_name=f"Level 3 - {cxo_user.role.capitalize()}"
        )
        print(f"\nSuccessfully triggered CXO email to {cxo_user.email} for Invoice {real_doc_id}")
    except Exception as e:
        print(f"\nError sending email: {e}")

if __name__ == '__main__':
    force_cxo_approval_and_email()
