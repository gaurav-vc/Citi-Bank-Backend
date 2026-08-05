import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from approvals.models import ApprovalRequest
from utils.email_helper import send_workflow_approval_email
from procurement.models import PaymentProposal, PurchaseOrder, Indent, RFQ, Invoice

User = get_user_model()

def check_and_trigger():
    # Find all active CXO users
    cxo_users = User.objects.filter(role__in=['cxo_citi', 'cxo_emb'], is_active=True)
    if not cxo_users.exists():
        print("No active CXO users found.")
        return

    # Check for pending approval requests assigned to any CXO user
    pending_approvals = ApprovalRequest.objects.filter(
        assigned_to__in=cxo_users,
        status='pending'
    )
    
    if not pending_approvals.exists():
        print("No pending approval requests for CXO users.")
        return
        
    print(f"Found {pending_approvals.count()} pending approval requests for CXOs.")
    
    for approval in pending_approvals:
        cxo_user = approval.assigned_to
        entity_type = approval.entity_type
        entity_id = approval.entity_id
        
        print(f"Processing approval {approval.id} for entity {entity_type} {entity_id} assigned to {cxo_user.email}")
        
        # Determine the module and document based on entity_type
        # ENTITY_TYPES = ['indent', 'purchase_order', 'grn', 'invoice', 'expense', 'payment']
        model_map = {
            'indent': ('indents', Indent, 'Indent'),
            'purchase_order': ('orders', PurchaseOrder, 'Purchase Order'),
            'invoice': ('invoices', Invoice, 'Invoice'),
            'payment': ('payments', PaymentProposal, 'Payment Proposal'),
            # other types mapping might be needed if they exist
        }
        
        if entity_type not in model_map:
            print(f"Entity type {entity_type} not handled for email yet.")
            continue
            
        real_module, model_class, title = model_map[entity_type]
        
        try:
            latest_doc = model_class.objects.get(id=entity_id)
        except model_class.DoesNotExist:
            print(f"Document {entity_id} for {entity_type} does not exist.")
            continue
            
        real_doc_id = str(latest_doc.id)
        
        # Safely extract amount
        v = getattr(latest_doc, 'net_value', None)
        if v is None: v = getattr(latest_doc, 'total_amount', None)
        if v is None: v = getattr(latest_doc, 'total_value', None)
        if v is None: v = getattr(latest_doc, 'estimated_value', None)
        if v is None: v = getattr(latest_doc, 'estimated_cost', 0.0)
        real_amount = float(v)
        
        # Determine vendor name if available
        vendor_name = "N/A"
        if getattr(latest_doc, 'vendor', None):
            try:
                from vendors.models import Vendor
                v_obj = Vendor.objects.filter(id=latest_doc.vendor).first()
                if v_obj:
                    vendor_name = getattr(v_obj, 'name', getattr(v_obj, 'company_name', 'Vendor'))
            except Exception:
                pass
        
        # Generate token for automatic login
        from rest_framework_simplejwt.tokens import AccessToken
        from datetime import timedelta
        from django.conf import settings
        
        token = AccessToken()
        token["user_id"] = str(cxo_user.id) if cxo_user.id else "1"
        token["role"] = cxo_user.role
        token["approval_role"] = cxo_user.role
        token["module"] = real_module
        token["document_id"] = real_doc_id
        token["approval_link"] = True
        token["purpose"] = "email_approval"

        token_lifetime_secs = getattr(settings, 'EMAIL_APPROVAL_TOKEN_LIFETIME_SECONDS', 3600)
        token.set_exp(lifetime=timedelta(seconds=token_lifetime_secs))
        
        # Build portal link dynamically based on the module
        if real_module == "payments":
            portal_link = f"https://procurement.vibesandbox.live/payments/proposals/{real_doc_id}?token={str(token)}"
        elif real_module == "orders":
            portal_link = f"https://procurement.vibesandbox.live/orders/{real_doc_id}?token={str(token)}"
        elif real_module == "indents":
            portal_link = f"https://procurement.vibesandbox.live/indents/{real_doc_id}?token={str(token)}"
        elif real_module == "rfqs":
            portal_link = f"https://procurement.vibesandbox.live/rfqs/{real_doc_id}?token={str(token)}"
        elif real_module == "invoices":
            portal_link = f"https://procurement.vibesandbox.live/billing/invoices/{real_doc_id}?token={str(token)}"
        else:
            portal_link = f"https://procurement.vibesandbox.live/dashboard?token={str(token)}"

        # Trigger the email template
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
            print(f"Successfully sent email to {cxo_user.email} for {title} {real_doc_id}")
        except Exception as e:
            print(f"Failed to send email to {cxo_user.email}: {e}")

if __name__ == '__main__':
    check_and_trigger()
