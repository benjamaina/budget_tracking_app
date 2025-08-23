from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework import serializers
import json
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from decimal import Decimal
from .models import (Event, BudgetItem, Pledge, MpesaPayment, ManualPayment, 
                     MpesaInfo, VendorPayment, ServiceProvider, Task, UserSettings)
from .serializers import (EventSerializer, BudgetItemSerializer, 
                          PledgeSerializer, ManualPaymentSerializer,
                            MpesaInfoSerializer,
                            VendorPaymentSerializer, ServiceProviderSerializer, 
                            RegisterSerializer, ChangePasswordSerializer,TaskSerializer,LoginSerializer, UserSettingsSerializer
)

from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import update_session_auth_hash
from datetime import date
from django.views.generic import TemplateView
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404





logger = logging.getLogger(__name__)



class UserSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        settings, created = UserSettings.objects.get_or_create(user=self.request.user)
        return settings

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)
        # return Event.objects.all()


class BudgetItemViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        print("Authenticated user:", self.request.user)
        return BudgetItem.objects.filter(user=self.request.user)
        # return BudgetItem.objects.all()

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Task.objects.filter(event_id=event_id, user=self.request.user)

    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_id')
        event = Event.objects.get(id=event_id)
        serializer.save(user=self.request.user, event=event)

class PledgeViewSet(viewsets.ModelViewSet):
    serializer_class = PledgeSerializer
    permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     event_id = self.kwargs.get('event_id')
    #     return Pledge.objects.filter(event_id=event_id, user = self.request.user)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        # event_id = self.kwargs.get('event_id')
        event_id = self.request.data.get('event')
        event = Event.objects.get(id=event_id)
        serializer.save(user=self.request.user, event=event)

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        if event_id:
            return Pledge.objects.filter(event_id=event_id, user=self.request.user)
        else:
            # fallback: all pledges for user, if event_id not provided
            return Pledge.objects.filter(user=self.request.user)

        
        
class ManualPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = ManualPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pledge_id = self.kwargs.get('pledge_id')
        return ManualPayment.objects.filter(pledge_id=pledge_id, user = self.request.user)

    def perform_create(self, serializer):
        pledge_id = self.kwargs.get('pledge_id')
        pledge = Pledge.objects.get(id=pledge_id)
        serializer.save(user=self.request.user, pledge=pledge)
        
class MpesaInfoView(viewsets.ModelViewSet):
    serializer_class = MpesaInfoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MpesaInfo.objects.filter(user=self.request.user)
    
    def get(self, request):
        mpesa_info = MpesaInfo.objects.filter(user=request.user).first()
        if mpesa_info:
            serializer = MpesaInfoSerializer(mpesa_info)
            return Response(serializer.data)
        return Response({"detail": "Mpesa info not found."}, status=status.HTTP_404_NOT_FOUND)
    
    

    def post(self, request):
        mpesa_info, _ = MpesaInfo.objects.get_or_create(user=request.user)
        serializer = MpesaInfoSerializer(mpesa_info, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VendorPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = VendorPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VendorPayment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ServiceProviderViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ServiceProvider.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        



class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response({"detail": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    # authentication_classes = []  # Disable authentication for this view

    def post(self, request, *args, **kwargs):
        print("Request method:", request.method)
        print("Request data:", request.data) 
        try:
            username = request.data.get("username")
            password = request.data.get("password")
            if not username or not password:
                return Response({"detail": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
            user = authenticate(username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_id": user.id,
                    "username": user.username
                })
            else:
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Login error: {e}")
            return Response({"detail": "Login failed."}, status=status.HTTP_400_BAD_REQUEST)



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Issue JWT token immediately
            refresh = RefreshToken.for_user(user)

            return Response({
                "user_id": user.id,
                "username": user.username,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Issue JWT token immediately
            refresh = RefreshToken.for_user(user)

            return Response({
                "user_id": user.id,
                "username": user.username,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        



class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = self.get_object()
        
        # Check old password 
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        
        # Update session to prevent logout
        update_session_auth_hash(request, user)
        
        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK
        )
    



class DashboardAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        user = request.user
        
        if pk:
            # Event-specific dashboard
            try:
                event = Event.objects.get(id=pk, user=user)
                return Response(self._get_event_data(event))
            except Event.DoesNotExist:
                return Response({"error": "Event not found"}, status=404)
        else:
            # General dashboard
            return Response(self._get_general_data(user))
    
    def _get_event_data(self, event):
        """Data for a single event dashboard"""
        return {
            'event': EventSerializer(event).data,
            'metrics': {
                'total_pledged': event.total_pledged(),
                'total_received': event.total_received(),
                'percentage_covered': event.percentage_covered(),
                'outstanding_balance': event.outstanding_balance(),
            },
            'pledges': PledgeSerializer(event.pledges.all(), many=True).data,
            'budget_items': BudgetItemSerializer(event.budget_items.all(), many=True).data,
            'tasks': TaskSerializer(Task.objects.filter(budget_item__event=event), many=True).data,
            'budget_summary': event.budget_summary(),
        }
    
    def _get_general_data(self, user):
        """Data for general dashboard"""
        now = timezone.now()
        events = Event.objects.filter(user=user)
        
        return {
            'summary': {
                'total_events': events.count(),
                'active_events': events.filter(event_date__gte=now.date()).count(),
                'funded_events': events.filter(is_funded=True).count(),
                'total_budget': events.aggregate(total=Sum('total_budget'))['total'] or 0,
            },
            'upcoming_events': EventSerializer(
                events.filter(event_date__gte=now.date()).order_by('event_date')[:5],
                many=True
            ).data,
        }