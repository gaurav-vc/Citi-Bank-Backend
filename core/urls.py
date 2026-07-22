from django.urls import path
from .views import DashboardMetricsView

urlpatterns = [
    path('dashboard/metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
]
