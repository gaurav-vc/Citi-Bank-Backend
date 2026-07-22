from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/setups/', include('setups.urls')),
    path('api/reports/', include('analytics.urls')),
    path('api/', include('access_control.urls')),
    path('api/', include('organizations.urls')),
    path('api/', include('procurement.urls')),
    path('api/', include('vendors.urls')),
    path('api/', include('inventory.urls')),
    path('api/', include('workflows.urls')),
    path('api/', include('core.urls')),
    path('api/', include('approvals.urls')),
]
