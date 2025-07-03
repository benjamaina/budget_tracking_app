# budgetapp/tests/factories.py

import factory
from faker import Faker
from django.contrib.auth import get_user_model
from budgetapp.models import Event, Donor, Pledge, BudgetItem, Task

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
    date = factory.LazyFunction(lambda: faker.date_object())  # Assuming this is a DateField
    time = factory.Faker("time")  # TimeField
    venue = factory.Faker("city")
    total_budget = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    created_by = factory.LazyAttribute(lambda obj: obj.user)
    description = factory.Faker("paragraph")


class DonorFactory(factory.django.DjangoModelFactory):
    """Internal use only: Not meant to be exposed directly."""
    class Meta:
        model = Donor

    user = factory.SubFactory(UserFactory)
    name = factory.Faker("name")
    phone_number = factory.Faker("phone_number")


class BudgetItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BudgetItem

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    category = factory.Faker("word")
    estimated_budget = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    is_funded = factory.Faker("boolean", chance_of_getting_true=50)


class PledgeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pledge

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    donor = factory.SubFactory(DonorFactory)
    is_fulfilled = factory.Faker("boolean", chance_of_getting_true=50)
    amount_pledged = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    user = factory.SubFactory(UserFactory)
    budget_item = factory.SubFactory(BudgetItemFactory, event__user=factory.SelfAttribute('..user'))
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    allocated_amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    amount_paid = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    due_date = factory.LazyFunction(lambda: faker.date_object())  # Assuming DateField
    completed = factory.Faker("boolean", chance_of_getting_true=50)
