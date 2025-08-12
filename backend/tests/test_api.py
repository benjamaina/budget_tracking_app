from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from budgetapp.models import (
    Event, BudgetItem, Pledge, MpesaPayment, 
    ManualPayment, MpesaInfo, VendorPayment, 
    ServiceProvider, Task
)
import datetime



class AuthSetupMixin:
    """Shared authentication setup for tests."""
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin', 
            email='admin@example.com', 
            password='adminpass123'
        )
        self.client.force_authenticate(user=self.user)

class EventAPITests(AuthSetupMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(
            name="Test Event", 
            user=self.user,
            total_budget=10000,
            event_date="2023-12-31"
        )
        self.url_list = reverse('event-list')
        self.url_detail = reverse('event-detail', args=[self.event.id])

    def test_create_event(self):
        data = {
            "name": "New Event",
            "total_budget": 5000,
            "event_date": "2023-11-15"
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Event.objects.last().user, self.user)

    def test_event_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_event_calculated_fields(self):
        Pledge.objects.create(
            event=self.event,
            user=self.user,
            amount_pledged=5000,
            name="Donor",
            phone_number="+254700000000"
        )
        MpesaPayment.objects.create(
            event=self.event,
            user=self.user,
            amount=3000,
            transaction_id="TEST123"
        )
        response = self.client.get(self.url_detail)
        self.assertEqual(Decimal(response.data['total_pledged']), Decimal('5000.00'))
        self.assertEqual(Decimal(response.data['total_received']), Decimal('3000.00'))

class BudgetItemAPITests(AuthSetupMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(
            name="Test Event",
            user=self.user,
            total_budget=10000,
            event_date="2023-12-31"
        )
        self.url_list = reverse('budget-item-list')

    def test_create_budget_item(self):
        data = {
            "event": self.event.id,
            "category": "Venue",
            "estimated_budget": 3000
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BudgetItem.objects.count(), 1)


    def test_budget_validation(self):
        
        BudgetItem.objects.create(
            event=self.event,
            user=self.user,
            category="Valid",
            estimated_budget=5000
        )
        
        
        data = {
            "event": self.event.id,
            "category": "Invalid",
            "estimated_budget": 6000  
        }
        response = self.client.post(self.url_list, data)

        assert response.status_code == 400
        assert "exceeds event's total budget" in response.data['__all__'][0]

     
class PledgeAPITests(AuthSetupMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(
            name="Test Event",
            user=self.user,
            total_budget=10000,
            event_date="2023-12-31"
        )
        self.pledge = Pledge.objects.create(
            event=self.event,
            user=self.user,
            amount_pledged=2000,
            name="Donor",
            phone_number="+254700000000"
        )
        self.url_list = reverse('pledge-list')
        self.url_detail = reverse('pledge-detail', args=[self.pledge.id])        

    def test_create_pledge(self):
        event = Event.objects.create(
            name="Pledge Test Event",
            user=self.user,
            total_budget=5000,
            event_date="2023-12-31"
        )
        
        data = {
            "event": event.id, 
            "amount_pledged": 3000,
            "name": "New Donor",
            "phone_number": "+254711111111"
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pledge.objects.count(), 2)


    def test_pledge_balance_calculation(self):
        # Create event first
        event = Event.objects.create(
            user=self.user,
            name="Test Event",
            description="Test Description",
            venue="Test Venue",
            total_budget=Decimal('10000.00'),
            event_date=datetime.date.today() + datetime.timedelta(days=30)
        )
        
        # Create pledge
        pledge = Pledge.objects.create(
            event=event,
            user=self.user,
            amount_pledged=2000,
            name="Test Donor",
            phone_number="+254722222222"
        )
        
        # Create payment
        MpesaPayment.objects.create(
            event=event,
            pledge=pledge,
            user=self.user,
            amount=1000,
            transaction_id="TEST123"
        )
        
        # Get pledge detail
        url = reverse('pledge-detail', kwargs={'pk': pledge.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['balance']), Decimal('1000.00'))


    def test_pledge_validation(self):
        # Create event first
        event = Event.objects.create(
            user=self.user,
            name="Validation Test Event",
            total_budget=5000,
            event_date="2023-12-31"
        )
        
        # Create a valid pledge
        data = {
            "event": event.id, 
            "amount_pledged": 3000,
            "name": "Valid Donor",
            "phone_number": "+254711111111"
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Attempt to create an invalid pledge that exceeds the event's budget
        data_invalid = {
            "event": event.id, 
            "amount_pledged": 6000,  # Exceeds total budget
            "name": "Invalid Donor",
            "phone_number": "+254722222222"
        }
        response_invalid = self.client.post(self.url_list, data_invalid)
        self.assertEqual(response_invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("exceeds event's total budget", response_invalid.data['non_field_errors'][0])

    def test_pledge_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Decimal(response.data[0]['amount_pledged']),self.pledge.amount_pledged)
        self.assertEqual(response.data[0]['name'], self.pledge.name)

    
        
class MpesaInfoAPITests(AuthSetupMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.mpesa_info = MpesaInfo.objects.create(
            user=self.user,
            paybill_number="123456",
            till_number="987654",
            account_name="Test Account"
        )
        self.url_list = reverse('mpesa-info-list')
        self.url_detail = reverse('mpesa-info-detail', kwargs={'pk': self.mpesa_info.id})

    def test_get_mpesa_info(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['paybill_number'], "123456")

    def test_update_mpesa_info(self):
        data = {
            "paybill_number": "654321",
            "till_number": "123456"
        }
        response = self.client.patch(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mpesa_info.refresh_from_db()
        self.assertEqual(self.mpesa_info.paybill_number, "654321")


class VendorPaymentAPITests(AuthSetupMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(
            name="Test Event",
            user=self.user,
            total_budget=10000,
            event_date="2023-12-31"
        )
        self.budget_item = BudgetItem.objects.create(
            event=self.event,
            user=self.user,
            category="Catering",
            estimated_budget=5000
        )
        self.service_provider = ServiceProvider.objects.create(
            budget_item=self.budget_item,
            user=self.user,
            service_type="Food",
            name="Test Caterer",
            phone_number="+254700000000",
            amount_charged=3000
        )
        self.url = reverse('vendorpayment-list')

    def test_create_vendor_payment(self):
        data = {
            "budget_item": self.budget_item.id,
            "service_provider": self.service_provider.id,
            "payment_method": "mpesa",
            "amount": 1000,
            "transaction_code": "VENDOR123"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(VendorPayment.objects.count(), 1)

class AuthAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.auth_urls = {
            'login': reverse('login'),
            'register': reverse('register'),
            'change_password': reverse('change-password')
        }

    def test_user_registration(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123"
        }
        response = self.client.post(self.auth_urls['register'], data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('access' in response.data)

    def test_login(self):
        data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = self.client.post(self.auth_urls['login'], data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
            
    def test_change_password(self):
    # Create test user
        user = User.objects.create_user(
            username='changepassword',
            password='oldpassword'
        )
        
        # Authenticate
        self.client.force_authenticate(user=user)
        
        # Test data
        data = {
            "old_password": "oldpassword",
            "new_password": "newpassword123"
        }
        
        # Make the request
        response = self.client.put(
            reverse('change-password'),
            data,
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "Password updated successfully."})
        
        # Verify password was actually changed
        user.refresh_from_db()
        self.assertTrue(
            user.check_password("newpassword123"),
            "New password was not set correctly"
        )
        
        # Verify old password no longer works
        self.assertFalse(
            user.check_password("oldpassword"),
            "Old password still works after change"
        )