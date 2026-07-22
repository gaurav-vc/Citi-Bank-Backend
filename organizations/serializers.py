from rest_framework import serializers
from .models import Organization, Site, Department, SiteModuleAccess

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

class SiteSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Site
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.name', read_only=True)

    class Meta:
        model = Department
        fields = '__all__'

class SiteModuleAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteModuleAccess
        fields = '__all__'

