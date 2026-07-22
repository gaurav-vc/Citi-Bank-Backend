from rest_framework.permissions import BasePermission
from setups.models import RoleAccessMapping
from access_control.models import Role

class RBACPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # 1. Super Admin has full system access
        if request.user.role == 'super_admin':
            return True

        # 2. CXO has full visibility but no destructive delete powers
        if request.user.role in ('cxo', 'cxo_citi', 'cxo_emb'):
            if request.method == 'DELETE':
                return False
            return True

        # 3. admin and client_admin can manage departments for their own site/org
        #    (site-scoping is enforced in the ViewSet's get_queryset/create)
        if request.user.role in ('admin', 'client_admin'):
            view_name = view.__class__.__name__
            if view_name in ('DepartmentViewSet', 'RoleViewSet'):
                return True

        view_name = view.__class__.__name__
        mapping_dict = {
            'VendorViewSet': 'procurement:vendors',
            'ItemViewSet': 'procurement:items',
            'RateContractViewSet': 'procurement:contracts',
            'BudgetViewSet': 'procurement:budgets',
            'IndentViewSet': 'procurement:indents',
            'RFQViewSet': 'procurement:rfqs',
            'PurchaseOrderViewSet': 'procurement:orders',
            'GRNViewSet': 'procurement:grn',
            'StockTransferViewSet': 'procurement:transfers',
            'MaterialIssueViewSet': 'procurement:material_issue',
            'ScrapDisposalViewSet': 'procurement:inventory',
            'InvoiceViewSet': 'procurement:billing',
            'PaymentProposalViewSet': 'procurement:payments',
            'ExpenseViewSet': 'procurement:expenses',
            'WorkflowViewSet': 'procurement:workflows',
            
            # Setup/master views
            'AppFeatureViewSet': 'core:users',
            'RoleAccessMappingViewSet': 'core:users',
            'FeatureMasterViewSet': 'core:users',
            'UsersHierarchyView': 'core:users',
            'AssignUserView': 'core:users',
            'OrganizationViewSet': 'core:organizations',
            'SiteViewSet': 'core:sites',
            'DepartmentViewSet': 'core:departments',
            'RoleViewSet': 'core:users',
        }

        feature_key = mapping_dict.get(view_name)
        if not feature_key:
            return True

        # Map HTTP method to action
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            action = 'view'
        elif request.method == 'POST':
            action = 'create'
        elif request.method in ('PUT', 'PATCH'):
            action = 'edit'
        elif request.method == 'DELETE':
            action = 'delete'
        else:
            return False

        try:
            role_obj = Role.objects.filter(role_name=request.user.role).first()
            if not role_obj:
                return False

            profile = getattr(request.user, 'profile', None)
            dept = getattr(profile, 'department', None) if profile else None
            mapping = None
            if dept:
                mapping = RoleAccessMapping.objects.filter(role=role_obj, department=dept).first()
            
            if not mapping:
                mapping = RoleAccessMapping.objects.filter(role=role_obj, department=None).first()
                
            if not mapping:
                return False

            permissions = mapping.permissions or {}
            
            # Allow users who can manage GRNs to view purchase orders for selection
            if feature_key == 'procurement:orders' and action == 'view':
                grn_perms = permissions.get('procurement:grn', {})
                if grn_perms.get('view') or grn_perms.get('create'):
                    return True

            feature_permissions = permissions.get(feature_key, {})
            
            # Support both 'edit' or 'update' checks
            return (
                feature_permissions.get(action) is True or 
                (action == 'edit' and feature_permissions.get('edit') is True) or
                (action == 'edit' and feature_permissions.get('update') is True)
            )
        except Exception as e:
            print(f"[RBAC ERROR] {request.user.email}: {e}")
            return False

def require_permission(feature_key, action):
    class DynamicPermission(BasePermission):
        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False
            if request.user.role == 'super_admin':
                return True
            if request.user.role in ('cxo', 'cxo_citi', 'cxo_emb'):
                if action == 'delete':
                    return False
                return True
            try:
                role_obj = Role.objects.filter(role_name=request.user.role).first()
                if not role_obj:
                    return False
                
                profile = getattr(request.user, 'profile', None)
                dept = getattr(profile, 'department', None) if profile else None
                mapping = None
                if dept:
                    mapping = RoleAccessMapping.objects.filter(role=role_obj, department=dept).first()
                
                if not mapping:
                    mapping = RoleAccessMapping.objects.filter(role=role_obj, department=None).first()
                    
                if not mapping:
                    return False
                permissions = mapping.permissions or {}
                feature_permissions = permissions.get(feature_key, {})
                return feature_permissions.get(action) is True
            except Exception as e:
                print("Permission check failed:", str(e))
                return False
    return DynamicPermission
