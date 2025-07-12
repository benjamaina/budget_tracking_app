from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, BudgetItemViewSet, PledgeViewSet, DashboardMetricsView, MpesaInfoView

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('budget-items/', BudgetItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='budget-item-list'),
    path('pledges/', PledgeViewSet.as_view({'get': 'list', 'post': 'create'}), name='pledge-list'),
    path('pledges/<int:pk>/', PledgeViewSet.as_view({'get': 'retrieve', 'put': 'update',    'delete': 'destroy'}), name='pledge-detail'),
    path('events/', EventViewSet.as_view({'get': 'list', 'post': 'create'}), name='event-list'),
    path('events/<int:pk>/', EventViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='event-detail'),
    path('mpesa-info/', MpesaInfoView.as_view({'get': 'list', 'post': 'create'}), name='mpesa-info-list'),
    path('dashboard/metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    
    
]
