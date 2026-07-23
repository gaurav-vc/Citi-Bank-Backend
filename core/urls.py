from django.urls import path
from .views import DashboardMetricsView, GlobalSearchView

urlpatterns = [
    path('dashboard/metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('search/', GlobalSearchView.as_view(), name='global-search'),
]
