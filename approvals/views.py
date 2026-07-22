from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import ApprovalRequest
from .serializers import ApprovalRequestSerializer

class ApprovalRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ApprovalRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ApprovalRequest.objects.filter(assigned_to=self.request.user)
        status_param = self.request.query_params.get('status', 'pending')
        if status_param and status_param != 'all':
            queryset = queryset.filter(status=status_param)
        return queryset

    @action(detail=False, methods=['get'], url_path='my-pending')
    def my_pending(self, request):
        queryset = ApprovalRequest.objects.filter(assigned_to=request.user, status='pending')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        # Allow updating status and remarks only
        allowed_keys = {'status', 'remarks'}
        # Filter request keys. If request.data is a QueryDict, we convert keys.
        keys = set(request.data.keys())
        extra_keys = keys - allowed_keys
        if extra_keys:
            raise ValidationError(f"Only status and remarks can be updated. Extra keys: {list(extra_keys)}")
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        approval = self.get_object()
        
        if 'remarks' in request.data:
            approval.remarks = request.data['remarks']

        # Multi-tier Finance Approval Chain Logic for Invoices
        if approval.entity_type == 'invoice':
            role_chain = ['finance_executive', 'finance_manager', 'cxo_citi', 'cxo_emb']
            current_role = request.user.role
            
            if current_role in role_chain:
                current_index = role_chain.index(current_role)
                if current_index < len(role_chain) - 1:
                    # Move to next approver
                    next_role = role_chain[current_index + 1]
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    next_approver = User.objects.filter(role=next_role).first()
                    
                    if next_approver:
                        approval.assigned_to = next_approver
                        approval.save()
                        return Response({
                            'status': 'Forwarded',
                            'message': f'Approval forwarded to {next_role.replace("_", " ").title()}'
                        })

            # Final approval step (or no next approver found)
            approval.status = 'approved'
            approval.save()

            # Update the Invoice status
            from procurement.models import Invoice, PaymentProposal
            import time
            from datetime import date
            invoice = Invoice.objects.filter(id=approval.entity_id).first()
            if invoice:
                invoice.status = 'approved'
                invoice.save()
                
                # Auto-generate Payment Proposal
                PaymentProposal.objects.create(
                    id=f"PAY-{int(time.time())}",
                    vendor_name=invoice.vendor_name,
                    vendor_id=invoice.vendor_id,
                    invoices=[{'invoice_id': invoice.id, 'amount': float(invoice.total_amount)}],
                    total_amount=invoice.total_amount,
                    net_payable=invoice.total_amount,
                    due_date=invoice.due_date,
                    created_date=date.today(),
                    status='pending_approval'
                )

        else:
            approval.status = 'approved'
            approval.save()

            try:
                from workflows.models import WorkflowInstance, WorkflowStep
                from workflows.engine import action_workflow_step

                entity_to_module = {
                    'indent': 'indents',
                    'purchase_order': 'orders',
                    'grn': 'grns',
                    'invoice': 'invoices',
                    'expense': 'expenses',
                    'payment': 'payments',
                }
                module_key = entity_to_module.get(approval.entity_type)
                if module_key:
                    instance = WorkflowInstance.objects.filter(module=module_key, entity_id=str(approval.entity_id)).first()
                    if instance:
                        step = WorkflowStep.objects.filter(
                            instance=instance,
                            assigned_role_name=request.user.role,
                            status='pending'
                        ).first()
                        if step:
                            action_workflow_step(
                                step.id,
                                'approve',
                                request.user,
                                comments=approval.remarks
                            )
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to advance workflow from ApprovalRequest: {e}")

        serializer = self.get_serializer(approval)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        approval = self.get_object()
        
        remarks = request.data.get('remarks', '').strip()
        if not remarks:
            raise ValidationError("Rejection reason is required before submitting the rejection.")
            
        approval.status = 'rejected'
        approval.remarks = remarks
        approval.save()

        if approval.entity_type != 'invoice':
            try:
                from workflows.models import WorkflowInstance, WorkflowStep
                from workflows.engine import action_workflow_step

                entity_to_module = {
                    'indent': 'indents',
                    'purchase_order': 'orders',
                    'grn': 'grns',
                    'invoice': 'invoices',
                    'expense': 'expenses',
                    'payment': 'payments',
                }
                module_key = entity_to_module.get(approval.entity_type)
                if module_key:
                    instance = WorkflowInstance.objects.filter(module=module_key, entity_id=str(approval.entity_id)).first()
                    if instance:
                        step = WorkflowStep.objects.filter(
                            instance=instance,
                            assigned_role_name=request.user.role,
                            status='pending'
                        ).first()
                        if step:
                            action_workflow_step(
                                step.id,
                                'reject',
                                request.user,
                                comments=remarks
                            )
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to reject workflow from ApprovalRequest: {e}")
        
        if approval.entity_type == 'invoice':
            from procurement.models import Invoice
            from django.utils import timezone
            
            invoice = Invoice.objects.filter(id=approval.entity_id).first()
            if invoice:
                invoice.status = 'rejected'
                invoice.rejected_by = request.user.email
                invoice.rejected_at = timezone.now()
                invoice.rejection_reason = remarks
                
                history_entry = {
                    'user': request.user.email,
                    'user_name': request.user.name if hasattr(request.user, 'name') else request.user.username,
                    'user_id': str(request.user.id),
                    'role': request.user.role,
                    'action': 'Reject',
                    'decision': 'Reject',
                    'comments': remarks,
                    'remarks': remarks,
                    'timestamp': timezone.now().isoformat()
                }
                if not invoice.workflow_history:
                    invoice.workflow_history = []
                invoice.workflow_history.append(history_entry)
                invoice.save()
                
                # Send email notification to the vendor
                try:
                    from utils.email_helper import send_invoice_rejection_email
                    from vendors.models import Vendor
                    vendor = Vendor.objects.filter(id=invoice.vendor_id).first()
                    vendor_email = vendor.email if (vendor and vendor.email) else 'vendor@example.com'
                    send_invoice_rejection_email(
                        vendor_email=vendor_email,
                        vendor_name=invoice.vendor_name,
                        invoice_number=invoice.invoice_number,
                        reason=remarks
                    )
                except Exception as email_err:
                    import logging
                    logging.getLogger(__name__).error(f"Failed to send rejection email: {str(email_err)}")
                    
                # Add audit trail entry for rejection
                try:
                    from vendors.models import AuditLog
                    AuditLog.objects.create(
                        action='INVOICE_REJECTED',
                        target_type='INVOICE',
                        target_id=str(invoice.id),
                        actioned_by=request.user.email,
                        comments=f"Invoice {invoice.invoice_number} rejected. Reason: {remarks}"
                    )
                except Exception as audit_err:
                    import logging
                    logging.getLogger(__name__).error(f"Failed to log rejection audit: {str(audit_err)}")

        serializer = self.get_serializer(approval)
        return Response(serializer.data)
