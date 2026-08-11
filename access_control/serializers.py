from rest_framework import serializers
from .models import Role, RoleModulePermission

class RoleSerializer(serializers.ModelSerializer):
    department_id = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = '__all__'

    def get_department_id(self, obj):
        from setups.models import RoleAccessMapping
        mapping = RoleAccessMapping.objects.filter(role=obj, department__isnull=False).first()
        return mapping.department.id if mapping else None

class RoleModulePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleModulePermission
        fields = '__all__'

