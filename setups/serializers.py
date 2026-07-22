from rest_framework import serializers
from .models import AppModule, AppFeature, RoleAccessMapping
from access_control.serializers import RoleSerializer
from organizations.serializers import DepartmentSerializer

class AppFeatureSerializer(serializers.ModelSerializer):
    key = serializers.CharField(source='feature_key', read_only=True)

    class Meta:
        model = AppFeature
        fields = ['id', 'feature_key', 'key', 'label', 'module']

class AppModuleSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    items = AppFeatureSerializer(source='features', many=True, read_only=True)

    class Meta:
        model = AppModule
        fields = ['id', 'title', 'module_order', 'items']

class RoleAccessMappingSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.role_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = RoleAccessMapping
        fields = '__all__'

from .models import InventoryMasterField

class InventoryMasterFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryMasterField
        fields = '__all__'
