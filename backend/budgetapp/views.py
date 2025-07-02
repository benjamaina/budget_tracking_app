from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from .models import Event, BudgetItem, Pledge, MpesaPayment
from .serializers import EventSerializer, BudgetItemSerializer, PledgeSerializer, MpesaPaymentSerializer
from django.db.models import Sum
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponseBadRequest
import json
import logging


logger = logging.getLogger(__name__)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer



class BudgetItemViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetItemSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return BudgetItem.objects.filter(event_id=event_id)


class PledgeViewSet(viewsets.ModelViewSet):
    serializer_class = PledgeSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Pledge.objects.filter(event_id=event_id)


@csrf_exempt
def mpesa_confirmation(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            logger.info(f"M-PESA Confirmation received: {data}")

            # Extract important info
            phone = data.get("MSISDN")
            amount = float(data.get("TransAmount"))
            transaction_id = data.get("TransID")

            # Handle logic (e.g. find matching pledge)
            # Update pledge model, etc.

            return JsonResponse({
                "ResultCode": 0,
                "ResultDesc": "Success"
            })

        except Exception as e:
            logger.error(f"Error: {e}")
            return JsonResponse({
                "ResultCode": 1,
                "ResultDesc": "Error"
            })



@method_decorator(csrf_exempt, name='dispatch')
class MpesaWebhookView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            logger.info(f"Incoming M-Pesa payment: {data}")

            # Extract relevant fields
            trans_id = data.get('TransID')
            phone = data.get('MSISDN')
            amount = float(data.get('TransAmount'))

            if not all([trans_id, phone, amount]):
                logger.warning("Missing data fields in request")
                return JsonResponse({"ResultCode": 1, "ResultDesc": "Missing fields"}, status=400)

            # Avoid duplicate transactions
            if MpesaPayment.objects.filter(transaction_id=trans_id).exists():
                logger.warning(f"Duplicate transaction detected: {trans_id}")
                return JsonResponse({"ResultCode": 0, "ResultDesc": "Already processed"})

            # Find matching pledge
            pledge = Pledge.objects.filter(phone_number=phone).order_by('-id').first()

            # Create payment record
            MpesaPayment.objects.create(
                pledge=pledge,
                phone_number=phone,
                amount=amount,
                transaction_id=trans_id
            )

            # Update pledge if found
            if pledge:
                pledge.amount_paid += amount
                pledge.is_fulfilled = pledge.amount_paid >= pledge.amount_pledged
                pledge.save()

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

        except Exception as e:
            logger.error(f"Error processing M-Pesa webhook: {str(e)}")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Server error"}, status=500)



class DashboardMetricsView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        event_id = kwargs['event_id']
        pledges = Pledge.objects.filter(event_id=event_id)
        items = BudgetItem.objects.filter(event_id=event_id)

        total_pledged = pledges.aggregate(total=Sum('amount_pledged'))['total'] or 0
        total_paid = pledges.aggregate(total=Sum('amount_paid'))['total'] or 0
        total_budget = items.aggregate(total=Sum('estimated_cost'))['total'] or 0

        return Response({
            'total_pledged': total_pledged,
            'total_paid': total_paid,
            'total_budget': total_budget,
            'percent_funded': (total_paid / total_budget * 100) if total_budget else 0
        })
