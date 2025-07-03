from django.test import TestCase
from budgetapp.serializers import EventSerializer, PledgeSerializer, BudgetItemSerializer, TaskSerializer
from .factories import EventFactory, DonorFactory, PledgeFactory, BudgetItemFactory, TaskFactory


class SerializerTests(TestCase):

    def test_event_serializer_fields(self):
        event = EventFactory()
        serializer = EventSerializer(event)
        data = serializer.data
        self.assertIn('name', data)
        self.assertIn('date', data)
        self.assertIn('time', data)
        self.assertIn('venue', data)
        self.assertIn('total_budget', data)
        self.assertIn('created_by', data)
        self.assertIn('description', data)


    def test_pledge_serializer_fields(self):
        pledge = PledgeFactory()
        serializer = PledgeSerializer(pledge)
        data = serializer.data
        self.assertIn('amount_pledged', data)
        self.assertIn('is_fulfilled', data)
        self.assertIn('event', data)
        self.assertIn('name', data)
        self.assertIn('phone_number', data)

    def test_budget_item_serializer_fields(self):
        budget_item = BudgetItemFactory()
        serializer = BudgetItemSerializer(budget_item)
        data = serializer.data
        self.assertIn('category', data)
        self.assertIn('estimated_budget', data)
        self.assertIn('is_funded', data)

    def test_task_serializer_fields(self):
        task = TaskFactory()
        serializer = TaskSerializer(task)
        data = serializer.data
        self.assertIn('title', data)
        self.assertIn('description', data)
        self.assertIn('allocated_amount', data)
        self.assertIn('amount_paid', data)
        self.assertIn('due_date', data)
        self.assertIn('completed', data)
