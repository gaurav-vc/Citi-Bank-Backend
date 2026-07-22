from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendorViewSet, RateContractViewSet

router = DefaultRouter()
router.register('vendors', VendorViewSet)
router.register('contracts', RateContractViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
