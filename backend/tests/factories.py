import factory
from faker import Faker
from django.contrib.auth import get_user_model
from budgetapp.models import (
    Event, BudgetItem, Pledge, MpesaPayment, ManualPayment,
    MpesaInfo, VendorPayment, ServiceProvider, Task
)

faker = Faker()
User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    user = factory.SubFactory(UserFactory)
    name = factory.Faker("sentence", nb_words=3)
    date = factory.LazyFunction(lambda: faker.date_object())
    time = factory.Faker("time")
    venue = factory.Faker("city")
    total_budget = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    created_by = factory.SelfAttribute("user")
    description = factory.Faker("paragraph")


class BudgetItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BudgetItem

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    category = factory.Faker("word")
    estimated_budget = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    is_funded = factory.Faker("boolean")


class PledgeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pledge

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    amount_pledged = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    name = factory.Faker("name")
    phone_number = factory.Faker("phone_number")
    total_paid = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)


class MpesaPaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MpesaPayment

    pledge = factory.SubFactory(PledgeFactory)
    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    transaction_id = factory.Faker("uuid4")


class ManualPaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ManualPayment

    pledge = factory.SubFactory(PledgeFactory)
    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)


class MpesaInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MpesaInfo

    checkout_request_id = factory.Faker("uuid4")
    merchant_request_id = factory.Faker("uuid4")
    response_code = factory.Faker("random_element", elements=["0", "1", "500"])
    response_description = factory.Faker("sentence")
    customer_message = factory.Faker("sentence")
    phone_number = factory.Faker("phone_number")


class ServiceProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ServiceProvider

    user = factory.SubFactory(UserFactory)
    name = factory.Faker("company")
    service_type = factory.Faker("word")
    phone_number = factory.Faker("phone_number")
    event = factory.SubFactory(EventFactory)


class VendorPaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VendorPayment

    service_provider = factory.SubFactory(ServiceProviderFactory)
    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    date = factory.LazyFunction(lambda: faker.date_object())


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    event = factory.SubFactory(EventFactory)
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    deadline = factory.LazyFunction(lambda: faker.future_date())
    assigned_to = factory.Faker("name")
    completed = factory.Faker("boolean")
