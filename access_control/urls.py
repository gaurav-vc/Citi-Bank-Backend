from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, RoleModulePermissionViewSet

router = DefaultRouter()
router.register('roles', RoleViewSet)
router.register('role-module-permissions', RoleModulePermissionViewSet)
router.register('role-permissions', RoleModulePermissionViewSet, basename='role-permissions')

urlpatterns = [
    path('', include(router.urls)),
]
