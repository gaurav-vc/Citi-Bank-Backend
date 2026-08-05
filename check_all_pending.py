import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from approvals.models import ApprovalRequest

def check_all_pending():
    pending_approvals = ApprovalRequest.objects.filter(status='pending')
    
    if not pending_approvals.exists():
        print("There are NO pending approval requests at all in the database.")
        return
        
    print(f"Found {pending_approvals.count()} total pending approval requests.")
    
    for approval in pending_approvals:
        assignee = approval.assigned_to
        role = assignee.role if assignee else 'Unassigned'
        email = assignee.email if assignee else 'N/A'
        print(f"ID: {approval.id} | Type: {approval.entity_type} {approval.entity_id} | Assigned To: {email} (Role: {role}) | Status: {approval.status}")

if __name__ == '__main__':
    check_all_pending()
