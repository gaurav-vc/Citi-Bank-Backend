from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowViewSet, WorkflowRuleViewSet

router = DefaultRouter()
router.register('workflows', WorkflowViewSet, basename='workflows')
router.register('workflow-rules', WorkflowRuleViewSet, basename='workflow-rules')

urlpatterns = [
    path('', include(router.urls)),
    path('workflows/pending', WorkflowViewSet.as_view({'get': 'pending'}), name='workflows-pending'),
    path('workflows/action', WorkflowViewSet.as_view({'post': 'action_step'}), name='workflows-action'),
    path('workflows/escalate', WorkflowViewSet.as_view({'post': 'escalate'}), name='workflows-escalate'),
]
