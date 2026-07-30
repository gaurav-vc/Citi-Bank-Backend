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
        # Trigger the professional email template we just updated
        send_workflow_approval_email(
            user=cxo_user,
            module_name="orders",                     # Simulating a Purchase Order
            document_id="PO-TEST-12345",              # Dummy Document ID
            title="Purchase Order",                   # Email Title
            portal_link="https://procurement.vibesandbox.live/dashboard", # Link to Portal
            created_by="system.admin@example.com",
            vendor_name="Global Tech Supplies",
            amount=150000.00,
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
