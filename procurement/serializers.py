from rest_framework import serializers
from .models import Indent, PurchaseOrder, Invoice, RFQ, Budget, Expense, PaymentProposal

class IndentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indent
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    rfq_workflow_history = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = '__all__'

    def get_rfq_workflow_history(self, obj):
        if obj.linked_rfq:
            try:
                rfq = RFQ.objects.filter(id=obj.linked_rfq).first()
                if rfq:
                    return rfq.workflow_history
            except Exception:
                pass
        return []

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class RFQSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQ
        fields = '__all__'

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

class PaymentProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProposal
        fields = '__all__'


from .models import Quotation, ItemCategory, BudgetRevisionLog

class QuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = '__all__'


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['id', 'code', 'name', 'description', 'is_active']


class BudgetRevisionLogSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.email', read_only=True)
    
    class Meta:
        model = BudgetRevisionLog
        fields = ['id', 'budget', 'previous_allocation', 'new_allocation', 'updated_by', 'updated_by_name', 'remarks', 'created_at']

