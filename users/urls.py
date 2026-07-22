from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView, RegisterView, UserProfileViewSet, MeView,
    UserViewSet, CompatibilityAssignUserView, ChangePasswordFirstLoginView
)

router = DefaultRouter()
router.register('profiles', UserProfileViewSet)
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login', LoginView.as_view(), name='login'),
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/change-password-first-login', ChangePasswordFirstLoginView.as_view(), name='change-password-first-login'),
    path('auth/me', MeView.as_view(), name='auth-me'),
    path('assign-user/', CompatibilityAssignUserView.as_view(), name='assign-user-compat'),
]

