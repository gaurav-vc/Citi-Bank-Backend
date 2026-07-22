from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AppFeatureViewSet, RoleAccessMappingViewSet, FeatureMasterViewSet,
    UsersHierarchyView, AssignUserView
)
from organizations.views import OrganizationViewSet, SiteViewSet, DepartmentViewSet

router = DefaultRouter()
router.register('app-features', AppFeatureViewSet)
router.register('role-access-mappings', RoleAccessMappingViewSet)

from .views import InventoryMasterFieldViewSet
router.register('inventory-master-fields', InventoryMasterFieldViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Custom routes mapping directly to the frontend fetches
    path('modules-features', FeatureMasterViewSet.as_view({'get': 'list'}), name='modules-features'),
    
    # Organizations, Sites, Departments mounted under setups to mirror Node/Express setup endpoints
    path('organizations', OrganizationViewSet.as_view({'get': 'list', 'post': 'create'}), name='setup-organizations'),
    path('sites', SiteViewSet.as_view({'get': 'list', 'post': 'create'}), name='setup-sites'),
    path('departments', DepartmentViewSet.as_view({'get': 'list', 'post': 'create'}), name='setup-departments'),
    path('users-hierarchy', UsersHierarchyView.as_view(), name='users-hierarchy'),
    path('users-hierarchy/', UsersHierarchyView.as_view(), name='users-hierarchy-slash'),
    path('assign-user', AssignUserView.as_view(), name='assign-user'),
    path('assign-user/', AssignUserView.as_view(), name='assign-user-slash'),
    path('role-access-mappings/sync_mapping', RoleAccessMappingViewSet.as_view({'post': 'sync_mapping'}), name='sync-mapping'),
]
