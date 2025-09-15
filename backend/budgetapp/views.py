# views.py
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
import logging
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
from django.db.models import Sum
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from django.db.models.deletion import ProtectedError
from rest_framework import status, serializers
from rest_framework.response import Response



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


class EventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })

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
    pagination_class = EventPagination

    

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    def get_queryset(self):
        try:
            user = self.request.user
            if not user or not user.is_authenticated:
                return Event.objects.none()  # return empty queryset instead of crashing
            return Event.objects.filter(user=user).order_by('-event_date', 'name')
        except Exception as e:
            logger.error(f"Error fetching events for user {self.request.user}: {e}")
            return Event.objects.none()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError as e:
            protected_objects = [str(obj) for obj in e.protected_objects]
            return Response(
                {
                    "detail": "Cannot delete because the following related objects exist.",
                    "related_objects": protected_objects,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

class BudgetItemViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for budget items tied to an event.
    Ensures validation errors are properly raised as DRF ValidationErrors.
    """
    serializer_class = BudgetItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination


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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError as e:
            protected_objects = [str(obj) for obj in e.protected_objects]
            return Response(
                {
                    "detail": "Cannot delete because the following related objects exist.",
                    "related_objects": protected_objects,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for tasks linked to budget items and events.
    """
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination

    def get_queryset(self):
        try:
            budget_item_id = self.kwargs.get('budget_item_id')
            if budget_item_id:
                return Task.objects.filter(budget_item_id=budget_item_id, user=self.request.user)
            return Task.objects.filter(user=self.request.user)
        except Exception as e:
            logger.error(f"Error fetching tasks for user {self.request.user}: {e}")
            return Task.objects.none()
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        


class PledgeViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for pledges towards events.
    """
    serializer_class = PledgeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination
    throttle_classes = [EventScopedThrottle, UserWriteThrottle]

    def retrieve(self, request, *args, **kwargs):
        """Custom retrieve to serialize single pledge."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Assign pledge to event and user on create."""
        try:
            event_id = self.request.data.get('event')
            event = Event.objects.get(id=event_id)
            serializer.save(user=self.request.user, event=event)
        except Event.DoesNotExist:
            raise serializers.ValidationError({"event": "Event does not exist."})
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        if event_id:
            return Pledge.objects.filter(event_id=event_id, user=self.request.user)
        return Pledge.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError as e:
            # Format the related objects into a nice error message
            protected_objects = [str(obj) for obj in e.protected_objects]
            raise serializers.ValidationError({
                "detail": "Cannot delete because the following related objects exist.",
                "related_objects": protected_objects
            })
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class MpesaPaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD for M-Pesa payments made by users.
    """
    serializer_class = MpesaPaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination

    def get_queryset(self):
        return MpesaPayment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class ManualPaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD for manual (non-M-Pesa) payments linked to pledges.
    """
    serializer_class = ManualPaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination

    def get_queryset(self):
        pledge_id = self.kwargs.get('pledge_id')
        if pledge_id:
            return ManualPayment.objects.filter(pledge_id=pledge_id, user=self.request.user)
        return ManualPayment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            pledge_id = self.kwargs.get('pledge_id')
            pledge = Pledge.objects.get(id=pledge_id)
            serializer.save(user=self.request.user, pledge=pledge)
        except Pledge.DoesNotExist:
            raise serializers.ValidationError({"pledge": "Pledge does not exist."})
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

class MpesaInfoView(viewsets.ModelViewSet):
    """
    Manage user-specific M-Pesa account information.
    Supports GET and POST for retrieval and updates.
    """
    serializer_class = MpesaInfoSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination

    def get_queryset(self):
        return VendorPayment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class ServiceProviderViewSet(viewsets.ModelViewSet):
    """
    Manage service providers linked to budget items.
    """
    serializer_class = ServiceProviderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination

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
    authentication_classes = [JWTAuthentication]
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


class RecentActivityView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # candidate timestamp field names (extend if your models use other names)
    TIMESTAMP_CANDIDATES = [
        "created_at", "created_on", "timestamp", "date_created", "created",
        "created_datetime", "created_date", "added", "time_created",
    ]

    def _get_ts_field(self, model):
        """Return the first timestamp-like field name present on the model, or None."""
        field_names = {f.name for f in model._meta.get_fields()}
        for cand in self.TIMESTAMP_CANDIDATES:
            if cand in field_names:
                return cand
        return None

    def _serialize_items(self, queryset, ts_field, kind, extra_fields):
        """
        Build a flattened list of dicts from queryset.
        `extra_fields` is list of model attribute names to include (e.g. ['name'] or ['amount_pledged']).
        Each item will have: type, id, created (ISO string), plus extra fields.
        """
        items = []
        for obj in queryset:
            ts_val = getattr(obj, ts_field) if ts_field else None
            # Normalize timestamp to ISO string; fallback to epoch-like string so sorting works.
            if hasattr(ts_val, "isoformat"):
                created = ts_val.isoformat()
            elif ts_val is None:
                created = "1970-01-01T00:00:00"
            else:
                created = str(ts_val)
            item = {"type": kind, "id": obj.id, "created": created}
            for f in extra_fields:
                item[f] = getattr(obj, f, None)
            items.append(item)
        return items

    def get(self, request):
        user = request.user
        cache_key = f"recent_activity:{user.id}"
        data = cache.get(cache_key)
        if data:
            return Response(data)

        # detect timestamp field per model
        event_ts = self._get_ts_field(Event)
        pledge_ts = self._get_ts_field(Pledge)
        payment_ts = self._get_ts_field(MpesaPayment)

        # order by detected timestamp or fallback to id
        event_order = f"-{event_ts}" if event_ts else "-id"
        pledge_order = f"-{pledge_ts}" if pledge_ts else "-id"
        payment_order = f"-{payment_ts}" if payment_ts else "-id"

        # fetch recent items (adjust slice sizes as desired)
        events_qs = Event.objects.filter(user=user).order_by(event_order)[:5]
        pledges_qs = Pledge.objects.filter(user=user).order_by(pledge_order)[:5]
        payments_qs = MpesaPayment.objects.filter(user=user).order_by(payment_order)[:5]

        activity = []
        # include 'name' for events, 'amount_pledged' for pledges (your model uses that), 'amount' for payments
        activity += self._serialize_items(events_qs, event_ts, "event", ["name"])
        activity += self._serialize_items(pledges_qs, pledge_ts, "pledge", ["amount_pledged"])
        activity += self._serialize_items(payments_qs, payment_ts, "payment", ["amount"])

        # sort by the ISO 'created' string descending and limit total items
        activity.sort(key=lambda x: x.get("created", "1970-01-01T00:00:00"), reverse=True)
        data = activity[:10]

        # cache for short period
        cache.set(cache_key, data, 30)
        return Response(data)
