# events/tests/test_api.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .factories import EventFactory, PledgeFactory, UserFactory, BudgetItemFactory, DonorFactory
from budgetapp.models import Event, Pledge, BudgetItem, Donor
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class EventAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        self.url = "/api/events/"  # update as needed

    def test_create_event(self):
        data = {
            "name": "Test Event",
            "description": "This is a test",
            "date": "2024-01-01",
            "time": "14:00:00",
            "venue": "Test Venue",
            "total_budget": "1000.00"
        }

        response = self.client.post(self.url, data, format="json")
        print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["created_by"], self.user.id)
        self.assertEqual(response.data["user"], self.user.id)


    def test_list_events(self):
        EventFactory(user=self.user, name="Event 1")
        EventFactory(user=self.user, name="Event 2")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_event(self):
        event = EventFactory(user=self.user, name="Test Event")
        url = reverse('event-detail', kwargs={'pk': event.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], event.name)
        self.assertEqual(response.data["created_by"], self.user.id)
        self.assertEqual(response.data["user"], self.user.id)


    def test_delete_event(self):
        event = EventFactory(user=self.user, name="Event to Delete")
        url = reverse('event-detail', kwargs={'pk': event.id})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

        # Verify the event is deleted
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_update_event(self):
        event = EventFactory(user=self.user, name="Old Event Name")
        url = reverse('event-detail', kwargs={'pk': event.id})

        data = {
            "name": "Updated Event Name",
            "description": "Updated description",
            "date": "2024-01-02",
            "time": "15:00:00",
            "venue": "Updated Venue",
            "total_budget": "2000.00"
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], data["name"])


    def test_unauthenticated_create_event(self):
        self.client.credentials()
        data = {
            "name": "Unauthenticated Event",
            "description": "This should fail",
            "date": "2024-01-01",
            "time": "14:00:00",
            "venue": "Test Venue",
            "total_budget": "1000.00"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 401)

        
    def test_user_can_access_own_events(self):
        event = EventFactory(user=self.user, name="My Event")
        url = reverse('event-detail', kwargs={'pk': event.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], event.name)
        self.assertEqual(response.data["created_by"], self.user.id)
        self.assertEqual(response.data["user"], self.user.id)

    def test_user_cannot_access_others_events(self):

        other_user = User.objects.create_user(username="other", password="pass")
        event = EventFactory(user=other_user, name="Other's Event")
        url = reverse('event-detail', kwargs={'pk': event.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
