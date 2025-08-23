from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (EventViewSet, BudgetItemViewSet, PledgeViewSet,
                     DashboardAPIView, MpesaInfoView, LoginView, 
                     LogoutView, RegisterView, ChangePasswordView,VendorPaymentViewSet, 
                     ManualPaymentViewSet,ServiceProviderViewSet, TaskViewSet, UserSettingsView
)
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('budget-items/', BudgetItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='budget-item-list'),
    path('budget-items/<int:pk>/', BudgetItemViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='budget-item-detail'),
    path('pledges/', PledgeViewSet.as_view({'get': 'list', 'post': 'create'}), name='pledge-list'),
    path('pledges/<int:pledge_id>/manual-payments/', ManualPaymentViewSet.as_view({'get': 'list', 'post': 'create'}), name='pledge-manual-payment-list'),
    path('pledges/<int:pk>/', PledgeViewSet.as_view({'get': 'retrieve', 'put': 'update',    'delete': 'destroy'}), name='pledge-detail'),
    path('events/', EventViewSet.as_view({'get': 'list', 'post': 'create'}), name='event-list'),
    path('events/<int:pk>/', EventViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='event-detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api-auth/', include('rest_framework.urls')), 
    path('register/', RegisterView.as_view(), name='register'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('mpesa-info/', MpesaInfoView.as_view({'get': 'list', 'post': 'create'}), name='mpesa-info-list'),
    path('mpesa-info/<int:pk>/', MpesaInfoView.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='mpesa-info-detail'),
    path('service-providers/', ServiceProviderViewSet.as_view({'get': 'list', 'post': 'create'}), name='service-provider-list'),
    path('service-providers/<int:pk>/', ServiceProviderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='service-provider-detail'),
    path('vendor-payments/', VendorPaymentViewSet.as_view({'get': 'list', 'post': 'create'}), name='vendorpayment-list'),
    path('dashboard/', DashboardAPIView.as_view(), name='general-dashboard'),
    path('dashboard/<int:pk>/', DashboardAPIView.as_view(), name='event-dashboard'),
    path('tasks/', TaskViewSet.as_view({'get': 'list', 'post': 'create'}), name='task-list'),
    path('tasks/<int:pk>/', TaskViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='task-detail'),
    path('user-settings/', UserSettingsView.as_view(), name='user-settings'),
    
     
    
]


