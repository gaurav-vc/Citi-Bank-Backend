from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardMetricsView, GlobalSearchView, FileUploadView, DocumentationViewSet, NotificationViewSet, AIAssistantView

router = DefaultRouter()
router.register(r'documentation', DocumentationViewSet, basename='documentation')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('search/', GlobalSearchView.as_view(), name='global-search'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('core/ai-assistant/', AIAssistantView.as_view(), name='ai-assistant'),
]
