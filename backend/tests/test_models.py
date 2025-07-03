# events/tests/test_models.py
from django.test import TestCase
from budgetapp.models import Event, Donor, Pledge, BudgetItem
from .factories import EventFactory, DonorFactory, PledgeFactory, BudgetItemFactory

class ModelTests(TestCase):
    def test_event_creation(self):
        event = EventFactory()
        self.assertIsInstance(event, Event)


    def test_pledge_linked_to_event_and_donor(self):
        pledge = PledgeFactory()
        self.assertIsNotNone(pledge.donor)
        self.assertIsNotNone(pledge.event)

    def test_budgetitem_amount_positive(self):
        item = BudgetItemFactory()
        self.assertGreater(item.estimated_budget, 0)
