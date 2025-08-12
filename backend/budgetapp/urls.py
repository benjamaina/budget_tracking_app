from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (EventViewSet, BudgetItemViewSet, PledgeViewSet,
                     DashboardMetricsView, MpesaInfoView, LoginView, LogoutView, RegisterView, ChangePasswordView,VendorPaymentViewSet
)
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('budget-items/', BudgetItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='budget-item-list'),
    path('budget-items/<int:pk>/', BudgetItemViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='budget-item-detail'),
    path('pledges/', PledgeViewSet.as_view({'get': 'list', 'post': 'create'}), name='pledge-list'),
    path('pledges/<int:pk>/', PledgeViewSet.as_view({'get': 'retrieve', 'put': 'update',    'delete': 'destroy'}), name='pledge-detail'),
    path('events/', EventViewSet.as_view({'get': 'list', 'post': 'create'}), name='event-list'),
    path('events/<int:pk>/', EventViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='event-detail'),
    path('mpesa-info/', MpesaInfoView.as_view({'get': 'list', 'post': 'create'}), name='mpesa-info-list'),
    path('dashboard/metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api-auth/', include('rest_framework.urls')), 
    path('register/', RegisterView.as_view(), name='register'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('mpesa-info/', MpesaInfoView.as_view({'get': 'list', 'post': 'create'}), name='mpesa-info-list'),
    path('mpesa-info/<int:pk>/', MpesaInfoView.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='mpesa-info-detail'),
    path('vendor-payments/', VendorPaymentViewSet.as_view({'get': 'list', 'post': 'create'}), name='vendorpayment-list'),
    
    
]


