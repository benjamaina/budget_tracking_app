from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from budgetapp.models import (Event, Pledge, MpesaPayment, ManualPayment, Task, 
                              MpesaInfo, VendorPayment, ServiceProvider, BudgetItem
)
from budgetapp.serializers import (EventSerializer, MpesaInfoSerializer, 
                                   PledgeSerializer, MpesaPaymentSerializer, 
                                   ManualPaymentSerializer, TaskSerializer, 
                                   VendorPaymentSerializer, ServiceProviderSerializer)


class AuthPermissionTests(APITestCase):
    def setUp(self):
        # Normal user
        self.user = User.objects.create_user(
            username="testuser", password="pass123"
        )
        # Another user (to test ownership restrictions)
        self.other_user = User.objects.create_user(

            username="otheruser", password="pass456"
        )
        # An event owned by self.user
        self.event = Event.objects.create(
            name="Test Event",
            user=self.user,
            total_budget=5000,
            event_date="2024-12-31"
        )
        self.url_detail = reverse("event-detail", args=[self.event.id])
        self.url_list = reverse("event-list")

    def test_event_list_requires_authentication(self):
        """Anonymous users should be blocked."""
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_event_retrieve_requires_owner(self):
        """User cannot retrieve another user's event."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # or 403 if you use explicit permission denial

    def test_event_delete_requires_owner(self):
        """Only the event owner can delete it."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url_detail)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_event_owner_can_delete(self):
        """Owner can delete their own event."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_event_create_requires_authentication(self):
        """Anonymous users should be blocked from creating events."""
        response = self.client.post(self.url_list, {
            "name": "New Event",
            "total_budget": 1000,
            "event_date": "2024-12-31"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            
    def test_event_create_authenticated_user(self):
        """Authenticated user can create an event."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url_list, {
            "name": "New Event",
            "total_budget": 1000,
            "event_date": "2024-12-31"
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 2)

        latest_event = Event.objects.order_by('-id').first()
        self.assertEqual(latest_event.name, "New Event")
        self.assertEqual(latest_event.user, self.user)

    def test_event_create_patch(self):
        """Authenticated user can update an event."""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url_detail, {
            "name": "Updated Event Name"
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.name, "Updated Event Name")

    def test_event_full_update(self):
        """Authenticated user can fully update an event."""
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url_detail, {
            "name": "Fully Updated Event",
            "total_budget": 6000,
            "event_date": "2025-01-01"
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.name, "Fully Updated Event")
        self.assertEqual(self.event.total_budget, 6000)
        self.assertEqual(str(self.event.event_date), "2025-01-01")

    def test_event_user_cannot_update_other_user_event(self):
        """User cannot update another user's event."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(self.url_detail, {
            "name": "Unauthorized Update"
        }, format='json')

        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_event_user_can_only_view_own_events(self):
        """User can only view their own events."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class TestPledgePermissions(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.other_user = User.objects.create_user(username="otheruser", password="pass456")
        self.event = Event.objects.create(
            name="Test Event",
            user=self.user,
            total_budget=5000,
            event_date="2024-12-31"
        )
        self.pledge = Pledge.objects.create(
            event=self.event,
            user=self.user,
            amount_pledged=1000,
            name ="Test Pledge",
            phone_number= 1234567890
        )
        self.url_detail = reverse("pledge-detail", args=[self.pledge.id])
        self.url_list = reverse("pledge-list")

    def test_pledge_list_requires_authentication(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pledge_retrieve_requires_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_pledge_delete_requires_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url_detail)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_pledge_owner_can_delete(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_pledge_create_requires_authentication(self):
        response = self.client.post(self.url_list, {
            "event": self.event.id,
            "amount_pledged": 500
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pledge_create_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url_list, {
            "event": self.event.id,
            "amount_pledged": 500,
            "name": "New Pledge",
            "phone_number": 9876543210
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pledge.objects.count(), 2)

    def test_pledge_create_patch(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url_detail, {
            "amount_pledged": 1200
        }, format='json')



class TestBudgetItemPermissions(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.other_user = User.objects.create_user(username="otheruser", password="pass456")
        self.event = Event.objects.create(
            name="Test Event",
            user=self.user,
            total_budget=5000,
            event_date="2024-12-31"
        )
        self.budget_item = BudgetItem.objects.create(
            event=self.event,
            category="Test Category",
            estimated_budget=1000,
            is_funded=True,
            user=self.user
        )
        self.url_detail = reverse("budget-item-detail", args=[self.budget_item.id])
        self.url_list = reverse("budget-item-list")

    def test_budget_item_list_requires_authentication(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_budget_item_retrieve_requires_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_budget_item_delete_requires_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url_detail)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_budget_item_owner_can_delete(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_budget_item_create_requires_authentication(self):
        response = self.client.post(self.url_list, {
            "event": self.event.id,
            "category": "New Category",
            "estimated_budget": 500
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_budget_item_create_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url_list, {
            "event": self.event.id,
            "category": "New Category",
            "estimated_budget": 500,
            "is_funded": True
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BudgetItem.objects.count(), 2)