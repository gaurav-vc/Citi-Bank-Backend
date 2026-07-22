from rest_framework import serializers
from .models import Vendor, RateContract

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class RateContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateContract
        fields = '__all__'
