from django.urls import path
from .views import ReportsDataView, ReportsExportView, AIInsightsView, SuperAdminDashboardView, SuperAdminBillingLogsView, SuperAdminBillingLogDetailView

urlpatterns = [
    path('super-admin-dashboard/', SuperAdminDashboardView.as_view(), name='super-admin-dashboard'),
    path('super-admin-billing-logs/', SuperAdminBillingLogsView.as_view(), name='super-admin-billing-logs'),
    path('super-admin-billing-logs/<int:pk>/', SuperAdminBillingLogDetailView.as_view(), name='super-admin-billing-log-detail'),
    path('data/', ReportsDataView.as_view(), name='reports-data'),
    path('export/<str:reportId>/', ReportsExportView.as_view(), name='reports-export'),
    path('ai-insights/', AIInsightsView.as_view(), name='reports-ai-insights'),
]
