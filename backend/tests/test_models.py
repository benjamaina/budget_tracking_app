
import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from budgetapp.models import (
    Event, BudgetItem, ServiceProvider, VendorPayment, Task, Pledge,
    MpesaPayment, ManualPayment, MpesaInfo
)


@pytest.mark.django_db
class TestModels:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="testuser", password="pass1234")

    @pytest.fixture
    def event(self, user):
        return Event.objects.create(
            user=user,
            name="Test Event",
            venue="Test Venue",
            description="Test Description",
            total_budget=Decimal("10000.00"),
            event_date=timezone.now().date()
        )

    @pytest.fixture
    def budget_item(self, user, event):
        return BudgetItem.objects.create(
            user=user,
            event=event,
            category="Catering",
            estimated_budget=Decimal("3000.00")
        )

    @pytest.fixture
    def service_provider(self, user, budget_item):
        return ServiceProvider.objects.create(
            user=user,
            budget_item=budget_item,
            service_type="Food",
            name="Best Caterers",
            phone_number="0712345678",
            email="test@example.com",
            amount_charged=Decimal("2800.00")
        )

    @pytest.fixture
    def vendor_payment(self, user, budget_item, service_provider):
        return VendorPayment.objects.create(
            user=user,
            budget_item=budget_item,
            service_provider=service_provider,
            payment_method="mpesa",
            transaction_code="TX1234567890",
            amount=Decimal("1000.00"),
            confirmed=True
        )

    @pytest.fixture
    def task(self, user, budget_item):
        return Task.objects.create(
            user=user,
            budget_item=budget_item,
            title="Setup Tent",
            description="Set up all tents before 8AM",
            allocated_amount=Decimal("1500.00"),
            amount_paid=Decimal("1000.00")
        )

    @pytest.fixture
    def pledge(self, user, event):
        return Pledge.objects.create(
            user=user,
            event=event,
            amount_pledged=Decimal("5000.00"),
            name="John Doe",
            phone_number="0712345678",
            total_paid=Decimal("2500.00")
        )

    @pytest.fixture
    def mpesa_payment(self, user, pledge, event):
        return MpesaPayment.objects.create(
            user=user,
            pledge=pledge,
            event=event,
            amount=Decimal("2000.00"),
            transaction_id="MPESA123456"
        )

    @pytest.fixture
    def manual_payment(self, user, pledge, event):
        return ManualPayment.objects.create(
            user=user,
            pledge=pledge,
            event=event,
            amount=Decimal("500.00"),
            date=timezone.now().date()
        )

    @pytest.fixture
    def mpesa_info(self, user):
        return MpesaInfo.objects.create(
            user=user,
            paybill_number="123456",
            till_number="654321",
            account_name="Test Account"
        )

    def test_event_creation(self, event):
        assert event.name == "Test Event"
        assert event.total_budget == Decimal("10000.00")

    def test_budget_item_creation(self, budget_item):
        assert budget_item.category == "Catering"

    def test_service_provider_creation(self, service_provider):
        assert service_provider.name == "Best Caterers"

    def test_vendor_payment_creation(self, vendor_payment):
        assert vendor_payment.amount == Decimal("1000.00")

    def test_task_creation(self, task):
        assert task.title == "Setup Tent"

    def test_pledge_creation(self, pledge):
        assert pledge.amount_pledged == Decimal("5000.00")

    def test_mpesa_payment_creation(self, mpesa_payment):
        assert mpesa_payment.transaction_id == "MPESA123456"

    def test_manual_payment_creation(self, manual_payment):
        assert manual_payment.amount == Decimal("500.00")

    def test_mpesa_info_creation(self, mpesa_info):
        assert mpesa_info.paybill_number == "123456"