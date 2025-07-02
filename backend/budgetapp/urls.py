from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, BudgetItemViewSet, PledgeViewSet, MpesaWebhookView, DashboardMetricsView

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('events/<int:event_id>/budget-items/', BudgetItemViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('events/<int:event_id>/pledges/', PledgeViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('mpesa/webhook/', MpesaWebhookView.as_view(), name='mpesa-webhook'),
    path('events/<int:event_id>/dashboard/', DashboardMetricsView.as_view(), name='dashboard'),
    
]
