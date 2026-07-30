import os
import django
import sys

# Setup Django environment
# Make sure to run this script from inside the Campusspend/backend directory
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

try:
    django.setup()
except Exception as e:
    print(f"Failed to setup Django. Make sure DJANGO_SETTINGS_MODULE is correct. Error: {e}")
    sys.exit(1)

from django.contrib.auth import get_user_model
from utils.email_helper import send_workflow_approval_email

User = get_user_model()

def trigger_test_email(target_email=None):
    # Find a CXO user in the database
    cxo_user = User.objects.filter(role__in=['cxo_citi', 'cxo_emb'], is_active=True).first()
    
    if not cxo_user:
        print("No active CXO user found in the database. Creating a mock user object in memory for testing.")
        cxo_user = User(
            email="mock_cxo@example.com",
            role="cxo_citi",
            is_active=True
        )
        # Mocking the name attribute which might be missing on base User
        cxo_user.name = "Mock CXO Officer"
    
    # If the user provides a specific email to test with, override it in memory
    if target_email:
        cxo_user.email = target_email

    print(f"\n--- Testing CXO Email Template ---")
    print(f"Sending to: {cxo_user.email} (Role: {cxo_user.role})")
    
    try:
        from procurement.models import PaymentProposal, PurchaseOrder, Indent, RFQ, Invoice
        
        candidates = []
        
        latest_payment = PaymentProposal.objects.order_by('-created_at').first()
        if latest_payment: candidates.append(('payments', latest_payment, 'Payment Proposal'))
            
        latest_po = PurchaseOrder.objects.order_by('-created_at').first()
        if latest_po: candidates.append(('orders', latest_po, 'Purchase Order'))
            
        latest_indent = Indent.objects.order_by('-created_at').first()
        if latest_indent: candidates.append(('indents', latest_indent, 'Indent'))
            
        latest_rfq = RFQ.objects.order_by('-created_at').first()
        if latest_rfq: candidates.append(('rfqs', latest_rfq, 'RFQ'))
            
        latest_invoice = Invoice.objects.order_by('-created_at').first()
        if latest_invoice: candidates.append(('invoices', latest_invoice, 'Invoice'))
        
        if not candidates:
            print("Could not find ANY documents in the live database. Create one first!")
            return
            
        # Sort by created_at descending to get the absolute most recent document you created
        candidates.sort(key=lambda x: getattr(x[1], 'created_at'), reverse=True)
        real_module, latest_doc, title = candidates[0]
        
        real_doc_id = str(latest_doc.id)
        
        # Safely extract amount regardless of what the field is named
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
        
        print(f"Found real document from Live DB: {real_module} -> {real_doc_id}")

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

        # Trigger the professional email template we just updated
        send_workflow_approval_email(
            user=cxo_user,
            module_name=real_module,
            document_id=real_doc_id,
            title=title,
            portal_link=portal_link,
            created_by="system.admin@example.com",
            vendor_name=vendor_name,
            amount=real_amount,
            stage_name="Level 3 - Cxo Citi"           # Contains 'cxo' so it triggers the executive template
        )
        print("\nSuccess! Email task has been dispatched.")
        print("Check your terminal (if using console email backend) or your actual inbox.")
    except Exception as e:
        print(f"\nError sending email: {e}")

if __name__ == "__main__":
    print("This script will send a test email using the CXO Professional Template.")
    test_email = input("Enter an email address to send the test to (or leave blank to use the DB user's email): ").strip()
    trigger_test_email(test_email if test_email else None)
