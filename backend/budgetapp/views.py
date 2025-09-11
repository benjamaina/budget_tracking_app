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
from .models import (
    Event, BudgetItem, Pledge, MpesaPayment, ManualPayment,
    MpesaInfo, VendorPayment, ServiceProvider, Task, UserSettings
)
from .serializers import (
    EventSerializer, BudgetItemSerializer, PledgeSerializer, 
    ManualPaymentSerializer, MpesaInfoSerializer, VendorPaymentSerializer, 
    ServiceProviderSerializer, RegisterSerializer, ChangePasswordSerializer, 
    TaskSerializer, LoginSerializer, UserSettingsSerializer, MpesaPaymentSerializer
)
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import update_session_auth_hash
from datetime import date, timedelta
from django.views.generic import TemplateView
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)



from rest_framework.throttling import SimpleRateThrottle, ScopedRateThrottle, AnonRateThrottle, UserRateThrottle

class LoginRateThrottle(SimpleRateThrottle):
    """
    Strict throttle for login endpoint. Keys by username+IP where possible.
    """
    scope = "login"

    def get_cache_key(self, request, view):
        if request.method != "POST":
            return None
        ident = self.get_ident(request)  # IP
        username = (request.data.get("username") or "").lower()
        # if username present, combine so attacking one account is limited per IP+user
        if username:
            return f"login:{username}:{ident}"
        return f"login:{ident}"

class UserWriteThrottle(SimpleRateThrottle):
    """
    Rate-limit write operations per authenticated user (fallback to IP for anon).
    """
    scope = "user_write"

    def get_cache_key(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return None
        if request.user and request.user.is_authenticated:
            return f"user_write:{request.user.pk}"
        return f"user_write:anon:{self.get_ident(request)}"

class EventScopedThrottle(SimpleRateThrottle):
    """
    Per-event per-user throttle (useful for pledges to stop spamming one event).
    Keys by event id (from kwargs/data) + user or IP.
    """
    scope = "pledge_per_event"

    def get_cache_key(self, request, view):
        # try URL kwarg -> request.data -> query param
        event_id = view.kwargs.get("event_id") or request.data.get("event") or request.query_params.get("event")
        if not event_id:
            # if no event in request, fall back to per-user key (or no throttle)
            if request.user and request.user.is_authenticated:
                return f"pledge:user:{request.user.pk}"
            return f"pledge:anon:{self.get_ident(request)}"
        user_part = request.user.pk if request.user and request.user.is_authenticated else self.get_ident(request)
        return f"pledge:event:{event_id}:user:{user_part}"




class UserSettingsView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve or update user-specific settings.

    - Uses `UserSettingsSerializer`.
    - Automatically creates settings for the user if they don’t exist.
    """
    serializer_class = UserSettingsSerializer
    permission_classes = [AllowAny]


    def get_object(self):
        settings, created = UserSettings.objects.get_or_create(user=self.request.user)
        return settings


class EventViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Events.
    Each event is linked to the authenticated user.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "event"


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        try:
            user = self.request.user
            if not user or not user.is_authenticated:
                return Event.objects.none()  # return empty queryset instead of crashing
            return Event.objects.filter(user=user)
        except Exception as e:
            logger.error(f"Error fetching events for user {self.request.user}: {e}")
            return Event.objects.none()


class BudgetItemViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for budget items tied to an event.
    Ensures validation errors are properly raised as DRF ValidationErrors.
    """
    serializer_class = BudgetItemSerializer
    uthentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]



    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return BudgetItem.objects.none()  # return empty queryset instead of crashing
        return BudgetItem.objects.filter(user=user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for tasks linked to budget items and events.
    """
    serializer_class = TaskSerializer
    uthentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Task.objects.filter(event_id=event_id, user=self.request.user)

    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_id')
        event = Event.objects.get(id=event_id)
        serializer.save(user=self.request.user, event=event)


class PledgeViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for pledges towards events.
    """
    serializer_class = PledgeSerializer
    uthentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        """Custom retrieve to serialize single pledge."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Assign pledge to event and user on create."""
        event_id = self.request.data.get('event')
        event = Event.objects.get(id=event_id)
        serializer.save(user=self.request.user, event=event)

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        if event_id:
            return Pledge.objects.filter(event_id=event_id, user=self.request.user)
        return Pledge.objects.filter(user=self.request.user)


class MpesaPaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD for M-Pesa payments made by users.
    """
    serializer_class = MpesaPaymentSerializer
    uthentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MpesaPayment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ManualPaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD for manual (non-M-Pesa) payments linked to pledges.
    """
    serializer_class = ManualPaymentSerializer
    uthentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pledge_id = self.kwargs.get('pledge_id')
        if pledge_id:
            return ManualPayment.objects.filter(pledge_id=pledge_id, user=self.request.user)
        return ManualPayment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        pledge_id = self.kwargs.get('pledge_id')
        pledge = Pledge.objects.get(id=pledge_id)
        serializer.save(user=self.request.user, pledge=pledge)


class MpesaInfoView(viewsets.ModelViewSet):
    """
    Manage user-specific M-Pesa account information.
    Supports GET and POST for retrieval and updates.
    """
    serializer_class = MpesaInfoSerializer
    uthentication_classes = [JWTAuthentication]
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
    """
    Manage payments to service providers for budget items.
    """
    serializer_class = VendorPaymentSerializer
    uthentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VendorPayment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ServiceProviderViewSet(viewsets.ModelViewSet):
    """
    Manage service providers linked to budget items.
    """
    serializer_class = ServiceProviderSerializer
    uthentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ServiceProvider.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LogoutView(generics.GenericAPIView):
    """
    Logout by blacklisting refresh tokens.
    """
    permission_classes = [AllowAny]

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
    """
    Custom login endpoint that authenticates with username & password.
    Returns JWT tokens if valid.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    # throttle_classes = [LoginRateThrottle]


    def post(self, request, *args, **kwargs):
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
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Login error: {e}")
            return Response({"detail": "Login failed."}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    Creates a new user and returns JWT tokens immediately.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "user_id": user.id,
                "username": user.username,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    """
    Allow authenticated users to change their password.
    Requires old password for validation.
    """
    uthentication_classes = [JWTAuthentication]
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
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        # Prevent session logout
        update_session_auth_hash(request, user)

        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)


class DashboardAPIView(APIView):
    """
    Provides dashboard data for:
    - A single event (if `pk` is provided).
    - General user dashboard (if no `pk`).
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user
        if pk:
            try:
                event = Event.objects.get(id=pk, user=user)
                return Response(self._get_event_data(event))
            except Event.DoesNotExist:
                return Response({"error": "Event not found"}, status=404)
        return Response(self._get_general_data(user))

    def _get_event_data(self, event):
        """Return data for single event dashboard."""
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
        """Return data for all events overview."""
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
        # Additional metrics can be added here as needed