from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import json
import logging

from .models import Event, BudgetItem, Pledge, MpesaPayment, ManualPayment, Donor
from .serializers import EventSerializer, BudgetItemSerializer, PledgeSerializer, MpesaPaymentSerializer, ManualPaymentSerializer

logger = logging.getLogger(__name__)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return Event.objects.filter(created_by=self.request.user)


class BudgetItemViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return BudgetItem.objects.filter(event_id=event_id)

    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_id')
        event = Event.objects.get(id=event_id)
        serializer.save(event=event)


class PledgeViewSet(viewsets.ModelViewSet):
    serializer_class = PledgeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Pledge.objects.filter(event_id=event_id)

    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_id')
        event = Event.objects.get(id=event_id)
        donor, _ = Donor.objects.get_or_create(
            phone_number=self.request.user.username,
            defaults={"name": self.request.user.get_full_name() or "Unnamed Donor"}
        )
        serializer.save(event=event, donor=donor)


class ManualPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = ManualPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pledge_id = self.kwargs.get('pledge_id')
        return ManualPayment.objects.filter(pledge_id=pledge_id)

    def perform_create(self, serializer):
        pledge_id = self.kwargs.get('pledge_id')
        pledge = Pledge.objects.get(id=pledge_id)
        donor, _ = Donor.objects.get_or_create(
            phone_number=self.request.user.username,
            defaults={"name": self.request.user.get_full_name() or "Unnamed Donor"}
        )
        serializer.save(pledge=pledge, donor=donor)


@method_decorator(csrf_exempt, name='dispatch')
class MpesaWebhookView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            logger.info(f"Incoming M-Pesa payment: {data}")

            trans_id = data.get('TransID')
            phone = data.get('MSISDN')
            try:
                amount = float(data.get('TransAmount'))
            except (TypeError, ValueError):
                return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid amount"}, status=400)

            if not all([trans_id, phone, amount]):
                return JsonResponse({"ResultCode": 1, "ResultDesc": "Missing fields"}, status=400)

            if MpesaPayment.objects.filter(transaction_id=trans_id).exists():
                return JsonResponse({"ResultCode": 0, "ResultDesc": "Already processed"})

            pledge = Pledge.objects.filter(donor__phone_number=phone).order_by('-id').first()

            MpesaPayment.objects.create(
                pledge=pledge,
                donor=pledge.donor if pledge else None,
                amount=amount,
                transaction_id=trans_id
            )

            if pledge:
                pledge.save()

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

        except Exception as e:
            logger.error(f"Error processing M-Pesa webhook: {str(e)}")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Server error"}, status=500)


class DashboardMetricsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        event_id = kwargs['event_id']
        pledges = Pledge.objects.filter(event_id=event_id)
        items = BudgetItem.objects.filter(event_id=event_id)

        total_pledged = pledges.aggregate(total=Sum('amount_pledged'))['total'] or 0
        total_paid = sum(p.total_paid() for p in pledges)
        total_budget = items.aggregate(total=Sum('estimated_budget'))['total'] or 0

        return Response({
            'total_pledged': total_pledged,
            'total_paid': total_paid,
            'total_budget': total_budget,
            'percent_funded': (total_paid / total_budget * 100) if total_budget else 0
        })
