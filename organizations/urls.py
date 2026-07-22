from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet, SiteViewSet, DepartmentViewSet,
    SiteModuleAccessViewSet, SiteAdminProvisionView
)

router = DefaultRouter()
router.register('organizations', OrganizationViewSet)
router.register('sites', SiteViewSet)
router.register('departments', DepartmentViewSet)
router.register('site-module-access', SiteModuleAccessViewSet)
router.register('site-modules', SiteModuleAccessViewSet, basename='site-modules')

urlpatterns = [
    # Custom views MUST come before router.urls to avoid the router's
    # sites/{pk}/ pattern swallowing 'provision-admin' as a pk lookup.
    path('provision-site-admin/', SiteAdminProvisionView.as_view(), name='site-provision-admin'),
    path('', include(router.urls)),
]
