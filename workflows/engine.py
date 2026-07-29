import logging
from django.utils import timezone
from django.db import transaction
from django.apps import apps
from django.contrib.auth import get_user_model
from .models import WorkflowInstance, WorkflowStep

logger = logging.getLogger(__name__)
User = get_user_model()

# Central registry mapping workflow module keys to Django model references
MODULE_MODELS = {
    'indents': 'procurement.Indent',
    'orders': 'procurement.PurchaseOrder',
    'invoices': 'procurement.Invoice',
    'expenses': 'procurement.Expense',
    'payments': 'procurement.PaymentProposal',
    'rfqs': 'procurement.RFQ',
    'budgets': 'procurement.Budget',
}

DEFAULT_WORKFLOWS = {
    'indents': [
        {'role': 'store_keeper', 'sla': 24},
        {'role': 'procurement_manager', 'sla': 24},
        {'role': 'facility_manager', 'sla': 24},
    ],
    'rfqs': [
        {'role': 'procurement_manager', 'sla': 24},
        {'role': 'facility_manager', 'sla': 24},
        {'role': 'project_head', 'sla': 24},
        {'role': 'cxo_citi', 'sla': 24},
        {'role': 'cxo_emb', 'sla': 24},
    ],
    'orders': [
        {'role': 'finance_executive', 'sla': 24},
        {'role': 'finance_manager', 'sla': 24},
        {'role': 'cxo_citi', 'sla': 24},
        {'role': 'cxo_emb', 'sla': 24},
    ],
    'invoices': [
        {'role': 'finance_executive', 'sla': 24},
        {'role': 'finance_manager', 'sla': 24},
        {'role': 'cxo_citi', 'sla': 24},
        {'role': 'cxo_emb', 'sla': 24},
    ],
    'expenses': [],
    'payments': [
        {'role': 'finance_manager', 'sla': 24},
        {'role': 'cxo_citi', 'sla': 24},
        {'role': 'cxo_emb', 'sla': 24},
    ],
    'budgets': [],
}

def get_model_class(module_key):
    model_path = MODULE_MODELS.get(module_key)
    if not model_path:
        raise ValueError(f"Unknown workflow module key: {module_key}")
    return apps.get_model(model_path)

def get_document(module_key, entity_id):
    model_class = get_model_class(module_key)
    return model_class.objects.get(id=entity_id)

def check_budget_utilisation(doc):
    try:
        from decimal import Decimal
        Budget = apps.get_model('procurement.Budget')
        category = getattr(doc, 'category', '')
        tower = getattr(doc, 'tower', '')
        dept = getattr(doc, 'department', '')
        v = getattr(doc, 'net_value', None)
        if v is None: v = getattr(doc, 'total_amount', None)
        if v is None: v = getattr(doc, 'total_value', None)
        if v is None: v = getattr(doc, 'estimated_value', None)
        if v is None: v = getattr(doc, 'estimated_cost', Decimal('0.00'))
        val = Decimal(str(v))
        
        budget = Budget.objects.filter(category__iexact=category, tower__iexact=tower).first()
        if not budget and dept:
            budget = Budget.objects.filter(department__iexact=dept).first()
        if not budget:
            budget = Budget.objects.filter(category__iexact=category).first()

        if budget:
            spent_or_committed = Decimal(str(budget.committed)) + Decimal(str(budget.actual))
            budget_limit = Decimal(str(budget.allocated)) if Decimal(str(budget.allocated)) > 0 else Decimal(str(budget.annual_budget))
            available = budget_limit - spent_or_committed
            utilization_pct = ((spent_or_committed + val) / budget_limit) * Decimal('100')
            
            if val > available:
                return False, f"Overspend Alert: Net value (₹{val:,.2f}) exceeds available budget (₹{available:,.2f}). Current utilization is at {utilization_pct:.1f}%.", float(utilization_pct), True
            
            if utilization_pct >= Decimal('90.0'):
                return True, f"Warning: Budget utilization is high ({utilization_pct:.1f}%). Remaining balance: ₹{available - val:,.2f}", float(utilization_pct), True
                
            return True, f"Budget verified. Utilization will be {utilization_pct:.1f}%. Remaining: ₹{available - val:,.2f}", float(utilization_pct), False
            
        return True, "No budget restriction defined.", 0.0, False
    except Exception as e:
        return True, f"Budget check bypassed: {str(e)}", 0.0, False

def update_budget_consumption(doc, action):
    try:
        from decimal import Decimal
        Budget = apps.get_model('procurement.Budget')
        category = getattr(doc, 'category', '')
        tower = getattr(doc, 'tower', '')
        v = getattr(doc, 'net_value', None)
        if v is None: v = getattr(doc, 'total_value', None)
        if v is None: v = getattr(doc, 'estimated_cost', None)
        if v is None: v = getattr(doc, 'total_amount', Decimal('0.00'))
        val = Decimal(str(v))
        
        budget = Budget.objects.filter(category__iexact=category, tower__iexact=tower).first()
        if not budget:
            budget = Budget.objects.filter(category__iexact=category).first()
            
        if budget:
            if action == 'commit':
                budget.committed = Decimal(str(budget.committed)) + val
            elif action == 'release':
                budget.committed = max(Decimal('0.00'), Decimal(str(budget.committed)) - val)
            elif action == 'actualize':
                budget.committed = max(Decimal('0.00'), Decimal(str(budget.committed)) - val)
                budget.actual = Decimal(str(budget.actual)) + val
            budget.save()
    except Exception as e:
        logger.error(f"Failed to update budget consumption: {str(e)}")
        raise e

@transaction.atomic
def initialize_workflow(module_key, entity_id, created_by_user):
    """
    Submits a document to the workflow engine, initializes steps, and updates fields.
    """
    doc = get_document(module_key, entity_id)
    doc.created_by = created_by_user.email
    prev_status = doc.status

    if module_key == 'indents':
        from rest_framework.exceptions import ValidationError
        from decimal import Decimal
        is_valid, msg, util_pct, is_overspent = check_budget_utilisation(doc)
        if is_overspent and not is_valid:
            Budget = apps.get_model('procurement.Budget')
            category = getattr(doc, 'category', '')
            tower = getattr(doc, 'tower', '')
            dept = getattr(doc, 'department', '')
            val = Decimal(str(getattr(doc, 'estimated_cost', Decimal('0.00'))))
            
            budget = Budget.objects.filter(category__iexact=category, tower__iexact=tower).first()
            if not budget and dept:
                budget = Budget.objects.filter(department__iexact=dept).first()
            if not budget:
                budget = Budget.objects.filter(category__iexact=category).first()
                
            if budget:
                spent_or_committed = Decimal(str(budget.committed)) + Decimal(str(budget.actual))
                budget_limit = Decimal(str(budget.allocated)) if Decimal(str(budget.allocated)) > 0 else Decimal(str(budget.annual_budget))
                available = budget_limit - spent_or_committed
                shortfall = val - available
                
                err_msg = (
                    f"Insufficient budget for this requisition.\n"
                    f"Available Budget: ₹{available:,.2f}\n"
                    f"Requested Amount: ₹{val:,.2f}\n"
                    f"Shortfall: ₹{shortfall:,.2f}"
                )
                raise ValidationError(err_msg)
    
    # Custom initial statuses for PO workflow
    if module_key == 'orders':
        doc.status = 'pending_finance_validation'
    elif module_key == 'indents':
        doc.status = 'pending_store_keeper'
    elif module_key == 'rfqs':
        doc.status = 'PROCUREMENT_MANAGER_REVIEW'
    else:
        doc.status = 'pending_approval'
        
    doc.approval_level = 1

    # Check for existing workflow instance
    instance, created = WorkflowInstance.objects.update_or_create(
        module=module_key,
        entity_id=str(entity_id),
        defaults={'status': 'pending'}
    )

    # Clean old steps
    WorkflowStep.objects.filter(instance=instance).delete()

    # For now, keep the hardcoded approval only. Dynamic configuration to be added later.
    hardcoded_rules = DEFAULT_WORKFLOWS.get(module_key, [])
    raw_steps = []
    for idx, rule in enumerate(hardcoded_rules):
        raw_steps.append({
            'role': rule['role'],
            'sla': rule['sla'],
            'sequence': idx + 1
        })

    # Validation to ensure users exist for all required roles in the workflow
    for rs in raw_steps:
        assigned_user = User.objects.filter(role=rs['role'], is_active=True).first()
        if not assigned_user:
            logger.warning(f"No user configured for role {rs['role']} in workflow {module_key}")

    sequence = 1
    steps_to_create = []
    
    for rs in raw_steps:
        due = timezone.now() + timezone.timedelta(hours=rs['sla'])
        
        assigned_user = None
        if rs['role'] == 'vendor' and module_key == 'orders':
            vendor_id = getattr(doc, 'vendor', None)
            if vendor_id:
                try:
                    from vendors.models import Vendor
                    vendor_obj = Vendor.objects.filter(id=vendor_id).first()
                    if vendor_obj and vendor_obj.email:
                        assigned_user = User.objects.filter(email=vendor_obj.email).first()
                except Exception as e:
                    logger.error(f"Failed to lookup vendor user: {e}")
        
        if not assigned_user:
            assigned_user = User.objects.filter(role=rs['role'], is_active=True).first()
            
        step = WorkflowStep(
            instance=instance,
            step_sequence=sequence,
            assigned_role_name=rs['role'],
            assigned_user=assigned_user,
            status='pending' if sequence == 1 else 'queued',
            sla_hours=rs['sla'],
            due_at=due
        )
        steps_to_create.append(step)
        sequence += 1

    WorkflowStep.objects.bulk_create(steps_to_create)

    # Set document routing state
    if steps_to_create:
        db_first_step = WorkflowStep.objects.filter(instance=instance, step_sequence=1).first()
        doc.current_approver = db_first_step.assigned_role_name if db_first_step else 'None'
        doc.next_role = steps_to_create[1].assigned_role_name if len(steps_to_create) > 1 else 'None'
    else:
        doc.current_approver = 'None'
        doc.next_role = 'None'
    
    doc.workflow_history = [{
        'user': created_by_user.email,
        'action': 'Submitted',
        'comments': 'Submitted for approval.',
        'timestamp': timezone.now().isoformat()
    }]
    if module_key == 'orders':
        if doc.status in ('approved', 'closed', 'vendor_accepted') and prev_status not in ('approved', 'closed', 'vendor_accepted'):
            update_budget_consumption(doc, 'commit')
    doc.save()

    if steps_to_create and db_first_step:
        try:
            trigger_next_approver_email(db_first_step, doc)
        except Exception as e:
            logger.error(f"Failed to trigger initial approver email: {e}")

    return doc

@transaction.atomic
def action_workflow_step(step_id, action_type, user, comments='', justification='', recommended_vendor='', decision=''):
    """
    Process an approval, rejection, hold or send back.
    """
    if action_type not in ('approve', 'reject', 'hold', 'send_back'):
        raise ValueError("Action must be 'approve', 'reject', 'hold', or 'send_back'")

    step = WorkflowStep.objects.select_related('instance').get(id=step_id)
    instance = step.instance
    doc = get_document(instance.module, instance.entity_id)
    prev_status = doc.status

    # Validate roles
    required_role = step.assigned_role_name
    user_role = user.role
    
    role_allowed = False
    if user_role == 'super_admin':
        role_allowed = True
    elif user_role == required_role:
        role_allowed = True
            
    if not role_allowed:
        raise PermissionError(f"Action requires role '{required_role}' (Current user role: '{user_role}', email: '{user.email}')")

    if action_type == 'hold':
        step.status = 'escalated'
        step.comments = f"[HOLD] {comments}"
    elif action_type == 'send_back':
        step.status = 'rejected'
        step.comments = f"[SEND BACK] {comments}"
    else:
        step.status = 'approved' if action_type == 'approve' else 'rejected'
        step.comments = comments
        
    step.actioned_at = timezone.now()
    step.actioned_by = user
    step.save()

    # Update corresponding ApprovalRequest if it exists
    try:
        from approvals.models import ApprovalRequest
        module_to_entity = {
            'indents': 'indent',
            'orders': 'purchase_order',
            'invoices': 'invoice',
            'expenses': 'expense',
            'payments': 'payment',
        }
        entity_type = module_to_entity.get(instance.module)
        if entity_type:
            ar = ApprovalRequest.objects.filter(
                entity_type=entity_type,
                entity_id=str(instance.entity_id),
                status='pending'
            ).first()
            if ar:
                ar.status = 'approved' if action_type == 'approve' else 'rejected'
                ar.remarks = comments
                ar.save()
    except Exception as e:
        logger.error(f"Failed to update corresponding ApprovalRequest: {e}")


    history_entry = {
        'user': user.email,
        'user_name': user.name if hasattr(user, 'name') else user.username,
        'user_id': str(user.id),
        'role': user.role,
        'action': action_type.capitalize() if action_type != 'send_back' else 'Send Back',
        'decision': decision or (action_type.capitalize() if action_type != 'send_back' else 'Send Back'),
        'recommended_vendor': recommended_vendor or getattr(doc, 'recommended_vendor_id', ''),
        'comments': comments,
        'remarks': comments,
        'justification': justification,
        'timestamp': timezone.now().isoformat()
    }
    
    if not doc.workflow_history:
        doc.workflow_history = []
    doc.workflow_history.append(history_entry)

    # Specific workflow logic for RFQs
    if instance.module == 'rfqs':
        if action_type == 'reject':
            if step.assigned_role_name in ('cxo_citi', 'cxo_emb'):
                # Return workflow to Procurement Manager (sequence 1)
                pm_step = WorkflowStep.objects.filter(instance=instance, assigned_role_name='procurement_manager').first()
                if pm_step:
                    pm_step.status = 'pending'
                    pm_step.actioned_at = None
                    pm_step.actioned_by = None
                    pm_step.comments = None
                    pm_step.save()
                    try:
                        trigger_next_approver_email(pm_step, doc)
                    except Exception:
                        pass
                
                # Reset other steps to queued
                WorkflowStep.objects.filter(instance=instance, step_sequence__gt=1).update(
                    status='queued', actioned_at=None, actioned_by=None, comments=None
                )
                
                doc.status = 'PROCUREMENT_MANAGER_REVIEW'
                doc.current_approver = 'procurement_manager'
                doc.next_role = 'facility_manager'
                doc.approval_level = 1
                doc.rejection_reason = comments
                doc.save()
                
                instance.status = 'REJECTED'
                instance.save()
                return doc
            else:
                # Rejecting at lower stages cancels workflow
                doc.status = 'REJECTED'
                doc.rejection_reason = comments
                doc.current_approver = None
                doc.next_role = None
                doc.save()
                instance.status = 'rejected'
                instance.save()
                WorkflowStep.objects.filter(instance=instance, status='pending').update(status='cancelled')
                return doc

        if action_type == 'send_back':
            if step.assigned_role_name in ('cxo_citi', 'cxo_emb'):
                # Return workflow to Project Head (sequence 3)
                ph_step = WorkflowStep.objects.filter(instance=instance, assigned_role_name='project_head').first()
                if ph_step:
                    ph_step.status = 'pending'
                    ph_step.actioned_at = None
                    ph_step.actioned_by = None
                    ph_step.comments = None
                    ph_step.save()
                    try:
                        trigger_next_approver_email(ph_step, doc)
                    except Exception:
                        pass
                
                # Reset CXO steps to queued
                WorkflowStep.objects.filter(instance=instance, assigned_role_name__in=['cxo_citi', 'cxo_emb']).update(
                    status='queued', actioned_at=None, actioned_by=None, comments=None
                )
                
                doc.status = 'PROJECT_HEAD_REVIEW'
                doc.current_approver = 'project_head'
                doc.next_role = 'None'
                doc.approval_level = 3
                doc.save()
            else:
                # Return workflow to previous stage
                prev_seq = step.step_sequence - 1
                prev_step = WorkflowStep.objects.filter(instance=instance, step_sequence=prev_seq).first()
                if prev_step:
                    prev_step.status = 'pending'
                    prev_step.actioned_at = None
                    prev_step.actioned_by = None
                    prev_step.comments = None
                    prev_step.save()
                    try:
                        trigger_next_approver_email(prev_step, doc)
                    except Exception:
                        pass
                    
                    doc.approval_level = prev_seq
                    doc.current_approver = prev_step.assigned_role_name
                    
                    if prev_step.assigned_role_name == 'procurement_manager':
                        doc.status = 'PROCUREMENT_MANAGER_REVIEW'
                    elif prev_step.assigned_role_name == 'facility_manager':
                        doc.status = 'FACILITY_MANAGER_REVIEW'
                    elif prev_step.assigned_role_name == 'project_head':
                        doc.status = 'PROJECT_HEAD_REVIEW'
                
                WorkflowStep.objects.filter(instance=instance, step_sequence__gte=step.step_sequence).update(
                    status='queued', actioned_at=None, actioned_by=None, comments=None
                )
                doc.save()
            return doc

        # Approve transition logic
        if action_type == 'approve':
            if step.assigned_role_name == 'procurement_manager':
                next_step = WorkflowStep.objects.filter(instance=instance, step_sequence=2).first()
                if next_step:
                    next_step.status = 'pending'
                    next_step.save()
                    try:
                        trigger_next_approver_email(next_step, doc)
                    except Exception:
                        pass
                doc.status = 'FACILITY_MANAGER_REVIEW'
                doc.current_approver = 'facility_manager'
                doc.next_role = 'project_head'
                doc.approval_level = 2
                doc.save()
                return doc

            elif step.assigned_role_name == 'facility_manager':
                next_step = WorkflowStep.objects.filter(instance=instance, step_sequence=3).first()
                if next_step:
                    next_step.status = 'pending'
                    next_step.save()
                    try:
                        trigger_next_approver_email(next_step, doc)
                    except Exception:
                        pass
                doc.status = 'PROJECT_HEAD_REVIEW'
                doc.current_approver = 'project_head'
                doc.next_role = 'None'
                doc.approval_level = 3
                doc.save()
                return doc

            elif step.assigned_role_name == 'project_head':
                # Activate parallel approvals for both CXOs (sequence 4 and 5)
                cxo_steps = WorkflowStep.objects.filter(instance=instance, assigned_role_name__in=['cxo_citi', 'cxo_emb'])
                for cs in cxo_steps:
                    cs.status = 'pending'
                    cs.due_at = timezone.now() + timezone.timedelta(hours=cs.sla_hours)
                    cs.save()
                    try:
                        trigger_next_approver_email(cs, doc)
                    except Exception:
                        pass
                doc.status = 'DUAL_CXO_REVIEW'
                doc.current_approver = 'cxo_citi, cxo_emb'
                doc.next_role = 'None'
                doc.approval_level = 4
                doc.save()
                return doc

            elif step.assigned_role_name in ('cxo_citi', 'cxo_emb'):
                other_cxo = 'cxo_emb' if step.assigned_role_name == 'cxo_citi' else 'cxo_citi'
                other_step = WorkflowStep.objects.filter(instance=instance, assigned_role_name=other_cxo).first()
                
                if other_step and other_step.status == 'approved':
                    doc.status = 'AWARD_READY'
                    doc.current_approver = None
                    doc.next_role = None
                    doc.approved_by = f"{other_step.actioned_by.email if other_step.actioned_by else ''}, {user.email}".strip(", ")
                    doc.approved_at = timezone.now()
                    doc.save()
                    instance.status = 'APPROVED_BY_BOTH_CXOS'
                    instance.save()
                else:
                    doc.status = 'WAITING_FOR_DUAL_CXO_APPROVAL'
                    doc.current_approver = other_cxo
                    doc.next_role = 'None'
                    doc.save()
                    if other_step:
                        try:
                            trigger_next_approver_email(other_step, doc)
                        except Exception:
                            pass
                return doc

    # Default transitions for other modules
    if action_type == 'reject':
        if not comments or not comments.strip():
            raise ValueError("Rejection reason is required before submitting the rejection.")

        doc.status = 'rejected'
        doc.rejection_reason = comments
        doc.rejected_by = user.email
        doc.rejected_at = timezone.now()
        doc.current_approver = None
        doc.next_role = None
        doc.save()

        instance.status = 'rejected'
        instance.save()

        if instance.module == 'orders':
            if prev_status in ('approved', 'closed', 'vendor_accepted'):
                update_budget_consumption(doc, 'release')

        if instance.module == 'invoices':
            # Send rejection email notification to the vendor
            try:
                from utils.email_helper import send_invoice_rejection_email
                from vendors.models import Vendor
                vendor = Vendor.objects.filter(id=doc.vendor_id).first()
                vendor_email = vendor.email if (vendor and vendor.email) else 'vendor@example.com'
                send_invoice_rejection_email(
                    vendor_email=vendor_email,
                    vendor_name=doc.vendor_name,
                    invoice_number=doc.invoice_number,
                    reason=comments
                )
            except Exception as email_err:
                logger.error(f"Failed to send invoice rejection email: {str(email_err)}")

            # Add an audit trail entry for the rejection
            try:
                from vendors.models import AuditLog
                AuditLog.objects.create(
                    action='INVOICE_REJECTED',
                    target_type='INVOICE',
                    target_id=str(doc.id),
                    actioned_by=user.email,
                    comments=f"Invoice {doc.invoice_number} rejected. Reason: {comments}"
                )
            except Exception as audit_err:
                logger.error(f"Failed to log rejection audit trail: {str(audit_err)}")

        if instance.module == 'payments':
            try:
                from vendors.models import Vendor
                vendor = Vendor.objects.filter(id=doc.vendor_id).first()
                vendor_email = vendor.email if (vendor and vendor.email) else 'vendor@example.com'
                from django.core.mail import send_mail
                from django.utils.html import strip_tags
                from utils.email_helper import get_email_base_html
                title = f"Payment Proposal Cancelled - Reference: {doc.id}"
                content_html = f"""
                <p>Dear Partner,</p>
                <p>We regret to inform you that the payment proposal <strong>{doc.id}</strong> has been cancelled/rejected during our internal review.</p>
                <div style="background-color:#F3F4F6;border:1px solid #E5E7EB;border-radius:6px;padding:15px;margin:20px 0;">
                  <p style="margin:0 0 6px 0;"><strong>Proposal Reference:</strong> {doc.id}</p>
                  <p style="margin:0 0 6px 0;"><strong>Net Amount:</strong> ₹{float(doc.net_payable):,.2f}</p>
                  <p style="margin:0;"><strong>Reason:</strong> {comments}</p>
                </div>
                <p>If you have any questions, please contact the finance team.</p>
                """
                html_message = get_email_base_html(title, content_html)
                plain_message = strip_tags(html_message)
                send_mail(
                    subject=title,
                    message=plain_message,
                    from_email='noreply.procurementdemo@gmail.com',
                    recipient_list=[vendor_email],
                    html_message=html_message,
                    fail_silently=False
                )
            except Exception as email_err:
                logger.error(f"Failed to send payment proposal cancellation email: {str(email_err)}")

        WorkflowStep.objects.filter(instance=instance, status='pending').update(status='cancelled')
        return doc

    # Parallel CXO Approval Check for Invoices and Payments
    if instance.module in ('invoices', 'payments') and step.assigned_role_name in ('cxo_citi', 'cxo_emb'):
        other_cxo = 'cxo_emb' if step.assigned_role_name == 'cxo_citi' else 'cxo_citi'
        other_step = WorkflowStep.objects.filter(instance=instance, assigned_role_name=other_cxo).first()
        
        if other_step and other_step.status == 'approved':
            # Both approved! Continue to approve the whole document
            doc.status = 'approved'
            if instance.module == 'invoices':
                update_budget_consumption(doc, 'actualize')
            doc.current_approver = None
            doc.next_role = None
            doc.approved_by = f"{other_step.actioned_by.email if other_step.actioned_by else ''}, {user.email}".strip(", ")
            doc.approved_at = timezone.now()
            doc.save()
            instance.status = 'approved'
            instance.save()
        else:
            doc.status = 'WAITING_FOR_DUAL_CXO_APPROVAL'
            doc.current_approver = other_cxo
            doc.next_role = 'None'
            doc.save()
            if other_step:
                try:
                    trigger_next_approver_email(other_step, doc)
                except Exception:
                    pass
        return doc

    next_step = WorkflowStep.objects.filter(
        instance=instance, 
        step_sequence=step.step_sequence + 1
    ).first()

    if next_step:
        if instance.module in ('invoices', 'payments') and next_step.assigned_role_name in ('cxo_citi', 'cxo_emb'):
            cxo_steps = WorkflowStep.objects.filter(instance=instance, assigned_role_name__in=['cxo_citi', 'cxo_emb'])
            for cs in cxo_steps:
                cs.status = 'pending'
                cs.due_at = timezone.now() + timezone.timedelta(hours=cs.sla_hours)
                cs.save()
                try:
                    trigger_next_approver_email(cs, doc)
                except Exception:
                    pass
            doc.status = 'DUAL_CXO_REVIEW'
            doc.current_approver = 'cxo_citi, cxo_emb'
            doc.next_role = 'None'
            doc.approval_level = next_step.step_sequence
            doc.save()
            return doc

        next_step.status = 'pending'
        next_step.due_at = timezone.now() + timezone.timedelta(hours=next_step.sla_hours)
        next_step.save()

        doc.approval_level = next_step.step_sequence
        doc.current_approver = next_step.assigned_role_name

        if instance.module == 'indents':
            if step.assigned_role_name == 'store_keeper':
                doc.status = 'pending_procurement_manager'
            elif step.assigned_role_name == 'procurement_manager':
                doc.status = 'pending_facility_manager'
        elif instance.module == 'orders':
            if next_step.assigned_role_name == 'vendor':
                doc.status = 'approved'
        
        future_step = WorkflowStep.objects.filter(
            instance=instance, 
            step_sequence=next_step.step_sequence + 1
        ).first()
        doc.next_role = future_step.assigned_role_name if future_step else 'None'
        doc.save()
        try:
            trigger_next_approver_email(next_step, doc)
        except Exception as e:
            logger.error(f"Failed to trigger next approver email: {e}")
    else:
        if instance.module == 'orders':
            doc.status = 'approved'
        else:
            doc.status = 'approved'
            if instance.module == 'invoices':
                update_budget_consumption(doc, 'actualize')
            
        doc.current_approver = None
        doc.next_role = None
        doc.approved_by = user.email
        doc.approved_at = timezone.now()
        if instance.module == 'orders':
            if doc.status in ('approved', 'closed', 'vendor_accepted') and prev_status not in ('approved', 'closed', 'vendor_accepted'):
                update_budget_consumption(doc, 'commit')
        doc.save()

        instance.status = 'approved'
        instance.save()
        
        # Send PO email to vendor upon final approval
        if instance.module == 'orders':
            try:
                import threading
                from utils.email_helper import send_po_creation_email
                threading.Thread(target=send_po_creation_email, args=(doc,)).start()
            except Exception as e:
                logger.error(f"Failed to send PO creation email after approval: {e}")

    return doc


def trigger_next_approver_email(step, doc):
    try:
        from utils.email_helper import send_workflow_approval_email
        from django.conf import settings
        
        user = step.assigned_user
        if not user:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(role=step.assigned_role_name, is_active=True).first()
            
        if not user:
            logger.warning(f"No user found for role {step.assigned_role_name} to send workflow email.")
            return
            
        module_name = step.instance.module
        document_id = doc.id
        title = f"{module_name[:-1].upper() if module_name.endswith('s') else module_name.upper()} Approval Required"
        
        # Build portal link
        from utils.email_helper import generate_portal_link
        portal_link = generate_portal_link(module_name, document_id)
        
        # Override link for CXO roles to point to relevant page with specific base URL
        user_role = getattr(user, 'role', '')
        if user_role in ('cxo_citi', 'cxo_emb') or step.assigned_role_name in ('cxo_citi', 'cxo_emb'):
            base_url = "http://localhost:8081"
            if module_name == 'rfqs':
                portal_link = f"{base_url}/tendering/rfq"
            elif module_name == 'invoices':
                portal_link = f"{base_url}/billing/invoices/{document_id}"
            elif module_name == 'payments':
                portal_link = f"{base_url}/payments/proposals/{document_id}"
            else:
                portal_link = f"{base_url}/dashboard"
                
            from rest_framework_simplejwt.tokens import AccessToken
            from datetime import timedelta
            token = AccessToken()
            token["user_id"] = str(user.id)
            token["role"] = user.role
            token["approval_role"] = step.assigned_role_name
            token["module"] = module_name
            token["document_id"] = str(doc.id)
            token["approval_link"] = True
            token["purpose"] = "email_approval"

            token_lifetime_secs = getattr(settings, 'EMAIL_APPROVAL_TOKEN_LIFETIME_SECONDS', 3600)
            token.set_exp(lifetime=timedelta(seconds=token_lifetime_secs))
            
            portal_link = f"{portal_link}?token={str(token)}"
        
        # Extract vendor and amount
        vendor_name = getattr(doc, 'vendor_name', None)
        amount = getattr(doc, 'estimated_cost', 
                         getattr(doc, 'net_value', 
                         getattr(doc, 'total_amount', 
                         getattr(doc, 'amount', None))))
                         
        created_by = getattr(doc, 'created_by', '')
        stage_name = f"Level {step.step_sequence} - {step.assigned_role_name.replace('_', ' ').title()}"
        
        send_workflow_approval_email(
            user=user,
            module_name=module_name,
            document_id=document_id,
            title=title,
            portal_link=portal_link,
            created_by=created_by,
            vendor_name=vendor_name,
            amount=amount,
            stage_name=stage_name
        )
    except Exception as e:
        logger.error(f"Failed to send workflow approval email for step {step.id}: {e}")
        # Create audit log entry for the failure
        try:
            from vendors.models import AuditLog
            AuditLog.objects.create(
                action='EMAIL_DELIVERY_FAILED',
                target_type=step.instance.module.upper(),
                target_id=str(doc.id),
                actioned_by='SYSTEM',
                comments=f"Failed to send workflow notification email to {getattr(user, 'email', 'unknown')}. Error: {str(e)}"
            )
        except Exception as audit_err:
            logger.error(f"Failed to write audit log for email failure: {audit_err}")

