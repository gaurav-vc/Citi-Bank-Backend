from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ItemViewSet, GRNViewSet, StockTransferViewSet,
    MaterialIssueViewSet, ScrapDisposalViewSet,
    StockLedgerView, InventoryExportView, InventoryImportView, AddStockView,
    InventoryHistoryView, QCGRNListView, QCGRNDetailView, QCGRNInspectView,
    ProductInspectionViewSet
)

router = DefaultRouter()
router.register('items', ItemViewSet)
router.register('grns', GRNViewSet)
router.register('transfers', StockTransferViewSet)
router.register('issues', MaterialIssueViewSet)
router.register('scrap', ScrapDisposalViewSet)
router.register('inspections', ProductInspectionViewSet)

urlpatterns = [
    path('stock/', StockLedgerView.as_view(), name='inventory-stock'),
    path('inventory/export/', InventoryExportView.as_view(), name='inventory-export'),
    path('inventory/import/', InventoryImportView.as_view(), name='inventory-import'),
    path('inventory/add-stock/', AddStockView.as_view(), name='inventory-add-stock'),
    path('inventory/<str:item_id>/history/', InventoryHistoryView.as_view(), name='inventory-history'),
    path('qc/grns/', QCGRNListView.as_view(), name='qc-grn-list'),
    path('qc/grns/<str:grn_id>/', QCGRNDetailView.as_view(), name='qc-grn-detail'),
    path('qc/grns/<str:grn_id>/inspect/', QCGRNInspectView.as_view(), name='qc-grn-inspect'),
    path('', include(router.urls)),
]
