from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from access_control.permissions import RBACPermission
from .models import AppModule, AppFeature, RoleAccessMapping
from .serializers import AppModuleSerializer, AppFeatureSerializer, RoleAccessMappingSerializer
from users.models import User, UserProfile

class AppFeatureViewSet(viewsets.ModelViewSet):
    queryset = AppFeature.objects.all()
    serializer_class = AppFeatureSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

class RoleAccessMappingViewSet(viewsets.ModelViewSet):
    queryset = RoleAccessMapping.objects.all()
    serializer_class = RoleAccessMappingSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        role_id = self.request.query_params.get('role')
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        return queryset

    @action(detail=False, methods=['post'])
    def sync_mapping(self, request):
        role_id = request.data.get('role_id')
        permissions_data = request.data.get('permissions', {})

        if not role_id:
            return Response({"error": "role_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            mapping, created = RoleAccessMapping.objects.update_or_create(
                role_id=role_id,
                defaults={'permissions': permissions_data}
            )
            return Response({"message": "Mapping synced successfully", "created": created})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FeatureMasterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AppModule.objects.prefetch_related('appfeature_set').all().order_by('module_order')
    serializer_class = AppModuleSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    # Map name field to title in query for frontend compatibility
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for mod in queryset:
            features = AppFeature.objects.filter(module=mod)
            items = [{"id": f.id, "feature_key": f.feature_key, "key": f.feature_key, "label": f.label} for f in features]
            data.append({
                "id": mod.id,
                "title": mod.name,
                "order": mod.module_order,
                "items": items
            })
        return Response(data)

class UsersHierarchyView(APIView):
    permission_classes = [IsAuthenticated, RBACPermission]

    def get(self, request):
        users = User.objects.all()
        data = []
        for u in users:
            org_name = ""
            site_name = ""
            dept_name = ""
            role_name = u.role
            
            # Retrieve profile fields if they exist
            profile = UserProfile.objects.filter(user=u).first()
            if profile:
                from organizations.models import Organization, Site, Department
                if profile.organization_id:
                    org = Organization.objects.filter(id=profile.organization_id).first()
                    if org: org_name = org.name
                if profile.site_id:
                    site = Site.objects.filter(id=profile.site_id).first()
                    if site: site_name = site.name
                if profile.department_id:
                    dept = Department.objects.filter(id=profile.department_id).first()
                    if dept: dept_name = dept.name
                if profile.role:
                    role_name = profile.role.role_name
                elif profile.role_name:
                    role_name = profile.role_name
            
            data.append({
                "user_id": str(u.id),
                "user_name": u.name,
                "email": u.email,
                "rbac_role": role_name,
                "organization_name": org_name,
                "site_name": site_name,
                "department_name": dept_name
            })
        return Response(data)

class AssignUserView(APIView):
    permission_classes = [IsAuthenticated, RBACPermission]

    def post(self, request):
        user_id = request.data.get('user_id')
        organization_id = request.data.get('organization_id')
        site_id = request.data.get('site_id')
        department_id = request.data.get('department_id')
        role_name = request.data.get('role_name')

        try:
            user = User.objects.get(id=user_id)
            if role_name:
                user.role = role_name
                user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.organization_id = organization_id
            profile.site_id = site_id
            profile.department_id = department_id
            if role_name:
                profile.role_name = role_name
            profile.save()

            return Response({"message": "User hierarchy assigned successfully"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from .models import InventoryMasterField
from .serializers import InventoryMasterFieldSerializer

class InventoryMasterFieldViewSet(viewsets.ModelViewSet):
    queryset = InventoryMasterField.objects.all()
    serializer_class = InventoryMasterFieldSerializer
    permission_classes = [AllowAny] # Using AllowAny for simpler integration, or IsAuthenticated based on setup
    
    def get_queryset(self):
        queryset = super().get_queryset()
        field_type = self.request.query_params.get('field_type')
        if field_type:
            queryset = queryset.filter(field_type=field_type)
        return queryset
