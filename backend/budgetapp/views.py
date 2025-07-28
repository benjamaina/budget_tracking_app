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
from decimal import Decimal
from .models import (Event, BudgetItem, Pledge, MpesaPayment, ManualPayment, 
                     MpesaInfo, VendorPayment, ServiceProvider, VendorCashPayment)
from .serializers import (EventSerializer, BudgetItemSerializer, 
                          PledgeSerializer, ManualPaymentSerializer,
                            MpesaInfoSerializer, VendorCashPaymentSerializer, 
                            VendorPaymentSerializer, ServiceProviderSerializer
)
logger = logging.getLogger(__name__)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)


class BudgetItemViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return BudgetItem.objects.filter(event_id=event_id, user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PledgeViewSet(viewsets.ModelViewSet):
    serializer_class = PledgeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Pledge.objects.filter(event_id=event_id, user = self.request.user)

    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_id')
        event = Event.objects.get(id=event_id)
        
        
class ManualPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = ManualPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pledge_id = self.kwargs.get('pledge_id')
        return ManualPayment.objects.filter(pledge_id=pledge_id, user = self.request.user)

    def perform_create(self, serializer):
        pledge_id = self.kwargs.get('pledge_id')
        pledge = Pledge.objects.get(id=pledge_id)
        
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
        

class VendorCashPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = VendorCashPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VendorCashPayment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# @method_decorator(csrf_exempt, name='dispatch')
# class MpesaWebhookView(View):
#     def post(self, request, *args, **kwargs):
#         try:
#             data = json.loads(request.body)
#             transaction_id = data.get('transaction_id')
#             amount = data.get('amount')
#             phone_number = data.get('phone_number')
#             paybill = data.get('paybill')  # Add this in payload!

#             if not all([transaction_id, amount, phone_number, paybill]):
#                 return JsonResponse({"error": "Missing required fields"}, status=400)

#             if MpesaPayment.objects.filter(transaction_id=transaction_id).exists():
#                 return JsonResponse({"message": "Transaction already recorded"}, status=200)

#             mpesa_info = MpesaInfo.objects.filter(paybill_number=paybill).first()
#             if not mpesa_info:
#                 return JsonResponse({"error": "No user found for that paybill"}, status=404)

#             user = mpesa_info.user

#             donor, _ = Donor.objects.get_or_create(user=user, phone_number=phone_number, defaults={"name": "Unknown Donor"})

#             pledge = Pledge.objects.filter(user=user, donor=donor).order_by('-id').first()

#             payment = MpesaPayment.objects.create(
#                 user=user,
#                 donor=donor,
#                 pledge=pledge,
#                 amount=Decimal(amount),
#                 transaction_id=transaction_id
#             )

#             return JsonResponse({"message": "Payment recorded", "payment_id": payment.id}, status=201)

#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON"}, status=400)
#         except Exception as e:
#             print(f"Webhook error: {e}")
#             return JsonResponse({"error": "Internal server error"}, status=500)


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
