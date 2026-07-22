from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IndentViewSet, PurchaseOrderViewSet, InvoiceViewSet,
    RFQViewSet, BudgetViewSet, ExpenseViewSet, PaymentProposalViewSet,
    download_purchase_order, QuotationViewSet, ItemCategoryViewSet
)

router = DefaultRouter()
router.register('indents', IndentViewSet, basename='indents')
router.register('requisitions/indents', IndentViewSet, basename='requisitions-indents')
router.register('orders', PurchaseOrderViewSet, basename='orders')
router.register('invoices', InvoiceViewSet, basename='invoices')
router.register('rfqs', RFQViewSet, basename='rfqs')
router.register('budgets', BudgetViewSet, basename='budgets')
router.register('expenses', ExpenseViewSet, basename='expenses')
router.register('payments', PaymentProposalViewSet, basename='payments')
router.register('quotations', QuotationViewSet, basename='quotations')
router.register('item-categories', ItemCategoryViewSet, basename='item-categories')

urlpatterns = [
    path('orders/<str:po_number>/download/', download_purchase_order),
    path('', include(router.urls)),
]
