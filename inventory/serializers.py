from rest_framework import serializers
from .models import Item, GRN, StockTransfer, MaterialIssue, ScrapDisposal

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class GRNSerializer(serializers.ModelSerializer):
    class Meta:
        model = GRN
        fields = '__all__'

class StockTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransfer
        fields = '__all__'

class MaterialIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialIssue
        fields = '__all__'

class ScrapDisposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapDisposal
        fields = '__all__'

from .models import GoodsDispatchNote, ReturnToVendor

class GoodsDispatchNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsDispatchNote
        fields = '__all__'

class ReturnToVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnToVendor
        fields = '__all__'

from .models import ProductInspection

class ProductInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInspection
        fields = '__all__'
