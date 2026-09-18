import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from procurement.models import RFQ
from workflows.models import WorkflowInstance, WorkflowStep

# Find unfinished RFQs
unfinished_rfqs = RFQ.objects.exclude(status__in=['AWARD_READY', 'REJECTED', 'rejected', 'approved'])
count = unfinished_rfqs.count()

print(f"Found {count} unfinished RFQs.")

if count > 0:
    rfq_ids = [str(r.id) for r in unfinished_rfqs]
    
    # Delete workflow steps and instances
    instances = WorkflowInstance.objects.filter(module='rfqs', entity_id__in=rfq_ids)
    step_count = WorkflowStep.objects.filter(instance__in=instances).delete()[0]
    inst_count = instances.delete()[0]
    
    print(f"Deleted {inst_count} WorkflowInstances and {step_count} WorkflowSteps.")
    
    # Delete the RFQs
    rfq_deleted_count = unfinished_rfqs.delete()[0]
    print(f"Successfully deleted {rfq_deleted_count} unfinished RFQs.")
else:
    print("No unfinished RFQs found to delete.")
