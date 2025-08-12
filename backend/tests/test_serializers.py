from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from budgetapp.models import (
    Event, BudgetItem, Pledge, MpesaPayment, 
    ManualPayment, Task, MpesaInfo, VendorPayment, ServiceProvider
)
from budgetapp.serializers import *
from decimal import Decimal
import datetime

class SerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.factory = APIRequestFactory()
        self.request = self.factory.post('/')
        self.request.user = self.user

        # Create test data
        self.event = Event.objects.create(
            user=self.user,
            name="Test Event",
            description="Test Description",
            venue="Test Venue",
            total_budget=Decimal('10000.00'),
            event_date=datetime.date.today() + datetime.timedelta(days=30)
        )
        
        self.budget_item = BudgetItem.objects.create(
            user=self.user,
            event=self.event,
            category="Catering",
            estimated_budget=Decimal('5000.00')
        )
        
        self.pledge = Pledge.objects.create(
            user=self.user,
            event=self.event,
            amount_pledged=Decimal('2000.00'),
            name="Test Pledger",
            phone_number="+254712345678"
        )
        
        self.service_provider = ServiceProvider.objects.create(
            user=self.user,
            budget_item=self.budget_item,
            service_type="Catering",
            name="Test Caterer",
            phone_number="+254712345679",
            amount_charged=Decimal('4000.00')
        )


class MpesaInfoSerializerTest(SerializerTestCase):
    def test_valid_mpesa_info_creation(self):
        data = {
            'paybill_number': '123456',
            'till_number': '987654',
            'account_name': 'Test Account'
        }
        serializer = MpesaInfoSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        mpesa_info = serializer.save()
        self.assertEqual(mpesa_info.user, self.user)
        self.assertEqual(mpesa_info.paybill_number, '123456')


class EventSerializerTest(SerializerTestCase):
    def test_event_serialization(self):
        serializer = EventSerializer(self.event, context={'request': self.request})
        expected_fields = [
            "id", "name", "description", "venue", "total_budget", "event_date",
            "user", "is_funded", "total_received", "total_pledged",
            "percentage_covered", "outstanding_balance", "overpaid_amount"
        ]
        self.assertEqual(set(serializer.data.keys()), set(expected_fields))
        self.assertEqual(serializer.data['name'], "Test Event")
    
    def test_event_creation(self):
        data = {
            "name": "New Event",
            "description": "New Description",
            "venue": "New Venue",
            "total_budget": "15000.00",
            "event_date": datetime.date.today() + datetime.timedelta(days=60)
        }
        serializer = EventSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        event = serializer.save()
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.total_budget, Decimal('15000.00'))

    def test_calculated_fields(self):
        # Add payments to test calculated fields
        MpesaPayment.objects.create(
            user=self.user,
            event=self.event,
            pledge=self.pledge,
            amount=Decimal('1000.00'),
            transaction_id="TEST123"
        )
        
        serializer = EventSerializer(self.event, context={'request': self.request})
        self.assertEqual(Decimal(serializer.data['total_received']), Decimal('1000.00'))
        self.assertEqual(Decimal(serializer.data['total_pledged']), Decimal('2000.00'))
        self.assertEqual(float(serializer.data['percentage_covered']), 50.0)


class BudgetItemSerializerTest(SerializerTestCase):
    def test_budget_item_serialization(self):
        serializer = BudgetItemSerializer(self.budget_item, context={'request': self.request})
        expected_fields = [
            'id', 'event', 'category', 'estimated_budget', 'is_funded',
            'total_vendor_payments', 'remaining_budget', 'is_fully_paid'
        ]
        self.assertEqual(set(serializer.data.keys()), set(expected_fields))
        self.assertEqual(serializer.data['category'], "Catering")
    
    def test_budget_item_creation(self):
        data = {
            "event": self.event.id,
            "category": "Venue",
            "estimated_budget": "3000.00"
        }
        serializer = BudgetItemSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        budget_item = serializer.save()
        self.assertEqual(budget_item.user, self.user)
        self.assertEqual(budget_item.estimated_budget, Decimal('3000.00'))
    
    def test_calculated_fields(self):
        # Add vendor payment to test calculated fields
        VendorPayment.objects.create(
            user=self.user,
            budget_item=self.budget_item,
            service_provider=self.service_provider,
            payment_method="mpesa",
            amount=Decimal('2000.00'),
            confirmed=True
        )
        
        serializer = BudgetItemSerializer(self.budget_item, context={'request': self.request})
        self.assertEqual(Decimal(serializer.data['total_vendor_payments']), Decimal('2000.00'))
        self.assertEqual(Decimal(serializer.data['remaining_budget']), Decimal('3000.00'))
        self.assertFalse(serializer.data['is_fully_paid'])


class PledgeSerializerTest(SerializerTestCase):
    def test_pledge_serialization(self):
        serializer = PledgeSerializer(self.pledge, context={'request': self.request})
        expected_fields = [
            'id', 'event', 'amount_pledged', 'is_fulfilled',
            'name', 'phone_number', 'user', 'total_paid', 'balance'
        ]
        self.assertEqual(set(serializer.data.keys()), set(expected_fields))
        self.assertEqual(serializer.data['name'], "Test Pledger")
    
    def test_pledge_creation(self):
        data = {
            "event": self.event.id,
            "amount_pledged": "3000.00",
            "name": "New Pledger",
            "phone_number": "+254712345670"
        }
        serializer = PledgeSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        pledge = serializer.save()
        self.assertEqual(pledge.user, self.user)
        self.assertEqual(pledge.amount_pledged, Decimal('3000.00'))
    
    def test_amount_validation(self):
        data = {
            "event": self.event.id,
            "amount_pledged": "0.00",
            "name": "Invalid Pledge",
            "phone_number": "+254712345670"
        }
        serializer = PledgeSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertEqual(
            serializer.errors['non_field_errors'][0],
            "Amount pledged must be greater than zero."
        )
    
    def test_balance_calculation(self):
        # Add payment to test balance calculation
        MpesaPayment.objects.create(
            user=self.user,
            event=self.event,
            pledge=self.pledge,
            amount=Decimal('500.00'),
            transaction_id="TEST456"
        )
        
        serializer = PledgeSerializer(self.pledge, context={'request': self.request})
        self.assertEqual(Decimal(serializer.data['total_paid']), Decimal('500.00'))
        self.assertEqual(Decimal(serializer.data['balance']), Decimal('1500.00'))


class MpesaPaymentSerializerTest(SerializerTestCase):
    def test_mpesa_payment_creation(self):
        data = {
            "event": self.event.id,
            "pledge": self.pledge.id,
            "amount": "1000.00",
            "transaction_id": "MPESA123"
        }
        serializer = MpesaPaymentSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        payment = serializer.save()
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.amount, Decimal('1000.00'))


class ManualPaymentSerializerTest(SerializerTestCase):
    def test_manual_payment_creation(self):
        data = {
            "event": self.event.id,
            "pledge": self.pledge.id,
            "amount": "500.00"
        }
        serializer = ManualPaymentSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        payment = serializer.save()
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.amount, Decimal('500.00'))
    
    def test_derived_fields(self):
        payment = ManualPayment.objects.create(
            user=self.user,
            event=self.event,
            pledge=self.pledge,
            amount=Decimal('500.00')
        )
        serializer = ManualPaymentSerializer(payment, context={'request': self.request})
        self.assertEqual(serializer.data['phone_number'], self.pledge.phone_number)
        self.assertEqual(serializer.data['name'], self.pledge.name)


class TaskSerializerTest(SerializerTestCase):
    def setUp(self):
        super().setUp()
        self.task = Task.objects.create(
            user=self.user,
            budget_item=self.budget_item,
            title="Test Task",
            description="Test Description",
            allocated_amount=Decimal('1000.00')
        )
    
    def test_task_serialization(self):
        serializer = TaskSerializer(self.task, context={'request': self.request})
        expected_fields = [
            'id', 'budget_item', 'title', 'description', 
            'allocated_amount', 'amount_paid', 'balance', 'user'
        ]
        self.assertEqual(set(serializer.data.keys()), set(expected_fields))
        self.assertEqual(serializer.data['title'], "Test Task")
    
    def test_task_creation(self):
        data = {
            "budget_item": self.budget_item.id,
            "title": "New Task",
            "description": "New Description",
            "allocated_amount": "500.00"
        }
        serializer = TaskSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.allocated_amount, Decimal('500.00'))
    
    def test_balance_calculation(self):
        serializer = TaskSerializer(self.task, context={'request': self.request})
        self.assertEqual(Decimal(serializer.data['balance']), Decimal('1000.00'))
        
        # Update amount paid
        self.task.amount_paid = Decimal('300.00')
        self.task.save()
        serializer = TaskSerializer(self.task, context={'request': self.request})
        self.assertEqual(Decimal(serializer.data['balance']), Decimal('700.00'))


class VendorPaymentSerializerTest(SerializerTestCase):
    def test_vendor_payment_creation(self):
        data = {
            "budget_item": self.budget_item.id,
            "service_provider": self.service_provider.id,
            "payment_method": "mpesa",
            "amount": "2000.00",
            "confirmed": True
        }
        serializer = VendorPaymentSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        payment = serializer.save()
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.amount, Decimal('2000.00'))


class ServiceProviderSerializerTest(SerializerTestCase):
    def test_service_provider_serialization(self):
        serializer = ServiceProviderSerializer(self.service_provider, context={'request': self.request})
        expected_fields = [
            'id', 'budget_item', 'service_type', 'name', 'phone_number',
            'email', 'amount_charged', 'total_received', 'balance_due', 'user'
        ]
        self.assertEqual(set(serializer.data.keys()), set(expected_fields))
        self.assertEqual(serializer.data['name'], "Test Caterer")
    
    def test_service_provider_creation(self):
        data = {
            "budget_item": self.budget_item.id,
            "service_type": "Venue",
            "name": "Test Venue Provider",
            "phone_number": "+254712345671",
            "amount_charged": "3000.00"
        }
        serializer = ServiceProviderSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        provider = serializer.save()
        self.assertEqual(provider.user, self.user)
        self.assertEqual(provider.amount_charged, Decimal('3000.00'))
    
    def test_calculated_fields(self):
        # Add payment to test calculated fields
        VendorPayment.objects.create(
            user=self.user,
            budget_item=self.budget_item,
            service_provider=self.service_provider,
            payment_method="mpesa",
            amount=Decimal('1000.00'),
            confirmed=True
        )
        
        serializer = ServiceProviderSerializer(self.service_provider, context={'request': self.request})
        self.assertEqual(Decimal(serializer.data['total_received']), Decimal('1000.00'))
        self.assertEqual(Decimal(serializer.data['balance_due']), Decimal('3000.00'))


class RegisterSerializerTest(TestCase):
    def test_user_registration(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpass123"
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")
    
    def test_password_write_only(self):
        serializer = RegisterSerializer()
        self.assertTrue(serializer.fields['password'].write_only)


class ChangePasswordSerializerTest(SerializerTestCase):
    def test_password_change_validation(self):
        data = {
            "old_password": "testpass123",
            "new_password": "newpass123"
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
    
    def test_old_password_validation(self):
        data = {
            "old_password": "wrongpass",
            "new_password": "newpass123"
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)
    
    def test_new_password_validation(self):
        data = {
            "old_password": "testpass123",
            "new_password": "short"
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)