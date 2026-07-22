from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import WorkflowInstance, WorkflowStep, WorkflowRule
from .serializers import WorkflowInstanceSerializer, WorkflowStepSerializer, WorkflowRuleSerializer
from .engine import initialize_workflow, action_workflow_step, get_document

class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = WorkflowInstance.objects.all()
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def pending(self, request):
        role = request.user.role
        
        steps = WorkflowStep.objects.filter(assigned_role_name=role, status='pending')
        
        # Enrich the steps with entity details
        enriched_data = []
        for step in steps:
            step_data = WorkflowStepSerializer(step).data
            try:
                instance = step.instance
                doc = get_document(instance.module, instance.entity_id)
                step_data['entity_details'] = {
                    'id': doc.id,
                    'module': instance.module,
                    'created_by': getattr(doc, 'created_by', ''),
                    'created_at': getattr(doc, 'created_at', timezone.now()).isoformat() if getattr(doc, 'created_at', None) else '',
                    'status': getattr(doc, 'status', ''),
                    'value': getattr(doc, 'estimated_cost', 
                                    getattr(doc, 'net_value', 
                                    getattr(doc, 'total_amount', 
                                    getattr(doc, 'amount', 0.0))))
                }
            except Exception as e:
                step_data['entity_details'] = None
            enriched_data.append(step_data)
            
        return Response(enriched_data)

    @action(detail=False, methods=['post'])
    def submit(self, request):
        module = request.data.get('module')
        entity_id = request.data.get('entity_id')
        if not module or not entity_id:
            return Response({"error": "module and entity_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            doc = initialize_workflow(module, entity_id, request.user)
            return Response({
                "message": f"Successfully submitted {module} document {entity_id} to workflow",
                "status": doc.status
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def action_step(self, request):
        step_id = request.data.get('step_id')
        action_type = request.data.get('action') # 'approve' or 'reject'
        comments = request.data.get('comments', '')
        justification = request.data.get('justification', '')
        recommended_vendor = request.data.get('recommended_vendor', '')
        decision = request.data.get('decision', '')

        if not step_id or not action_type:
            return Response({"error": "step_id and action are required"}, status=status.HTTP_400_BAD_REQUEST)
        if action_type not in ('approve', 'reject', 'hold', 'send_back'):
            return Response({"error": "action must be approve, reject, hold, or send_back"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate approval token if present
        is_approval_token = False
        if request.auth:
            try:
                is_approval_token = request.auth.get('approval_link') is True or request.auth.get('purpose') == 'email_approval'
            except Exception:
                pass

        if is_approval_token:
            try:
                token_user_id = str(request.auth.get('user_id'))
                token_role = request.auth.get('role')
                token_approval_role = request.auth.get('approval_role')
                token_module = request.auth.get('module')
                token_doc_id = str(request.auth.get('document_id'))
                token_purpose = request.auth.get('purpose')
                token_approval_link = request.auth.get('approval_link')

                step = WorkflowStep.objects.get(id=step_id)
                instance = step.instance

                if (not token_approval_link or 
                    token_purpose != 'email_approval' or 
                    token_user_id != str(request.user.id) or 
                    token_role != request.user.role or 
                    token_approval_role != step.assigned_role_name or 
                    token_module != instance.module or 
                    token_doc_id != str(instance.entity_id)):
                    
                    return Response(
                        {"detail": "Invalid or expired approval link."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Exception:
                return Response(
                    {"detail": "Invalid or expired approval link."},
                    status=status.HTTP_403_FORBIDDEN
                )

        try:
            doc = action_workflow_step(
                step_id, 
                action_type, 
                request.user, 
                comments=comments, 
                justification=justification, 
                recommended_vendor=recommended_vendor, 
                decision=decision
            )
            return Response({
                "message": f"Successfully actioned step: {action_type}",
                "document_status": doc.status
            })
        except PermissionError as pe:
            return Response({"error": str(pe)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def timeline(self, request):
        module = request.query_params.get('module')
        entity_id = request.query_params.get('entity_id')
        if not module or not entity_id:
            return Response({"error": "module and entity_id query parameters are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            instance = WorkflowInstance.objects.get(module=module, entity_id=entity_id)
            steps = WorkflowStep.objects.filter(instance=instance).order_by('step_sequence')
            
            # Retrieve document metadata for current state
            doc = get_document(module, entity_id)
            doc_info = {
                'status': getattr(doc, 'status', ''),
                'current_approver': getattr(doc, 'current_approver', ''),
                'next_role': getattr(doc, 'next_role', ''),
                'workflow_history': getattr(doc, 'workflow_history', []),
                'approval_level': getattr(doc, 'approval_level', 0),
                'approved_by': getattr(doc, 'approved_by', ''),
                'approved_at': getattr(doc, 'approved_at', None),
                'rejection_reason': getattr(doc, 'rejection_reason', '')
            }

            return Response({
                "instance": WorkflowInstanceSerializer(instance).data,
                "steps": WorkflowStepSerializer(steps, many=True).data,
                "document": doc_info
            })
        except WorkflowInstance.DoesNotExist:
            try:
                doc = get_document(module, entity_id)
                doc_status = getattr(doc, 'status', '')
                if doc_status in ('approved', 'active', 'completed'):
                    doc_info = {
                        'status': doc_status,
                        'current_approver': getattr(doc, 'current_approver', ''),
                        'next_role': getattr(doc, 'next_role', ''),
                        'workflow_history': getattr(doc, 'workflow_history', []),
                        'approval_level': getattr(doc, 'approval_level', 0),
                        'approved_by': getattr(doc, 'approved_by', ''),
                        'approved_at': getattr(doc, 'approved_at', None),
                        'rejection_reason': getattr(doc, 'rejection_reason', '')
                    }
                    return Response({
                        "instance": {
                            "module": module,
                            "entity_id": entity_id,
                            "status": "approved"
                        },
                        "steps": [],
                        "document": doc_info
                    })
            except Exception:
                pass
            return Response({"message": "No active workflow for this entity"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def escalate(self, request):
        overdue_steps = WorkflowStep.objects.filter(status='pending', due_at__lt=timezone.now())
        count = 0
        for step in overdue_steps:
            step.status = 'escalated'
            hierarchy = {
                'store_keeper': 'procurement_executive',
                'procurement_executive': 'procurement_manager',
                'procurement_manager': 'cxo',
                'finance_executive': 'finance_manager',
                'finance_manager': 'cxo',
                'site_engineer': 'facility_manager',
                'facility_manager': 'project_head'
            }
            next_role = hierarchy.get(step.assigned_role_name, 'cxo')
            step.escalated_to_role = next_role
            step.save()
            count += 1
        return Response({"message": f"Escalated {count} overdue steps."})

class WorkflowRuleViewSet(viewsets.ModelViewSet):
    queryset = WorkflowRule.objects.all().order_by('module', 'step_sequence')
    serializer_class = WorkflowRuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        module = self.request.query_params.get('module')
        if module:
            queryset = queryset.filter(module=module)
        return queryset
