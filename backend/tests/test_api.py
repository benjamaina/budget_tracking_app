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

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["created_by"], self.user.id)
        self.assertEqual(response.data["user"], self.user.id)
