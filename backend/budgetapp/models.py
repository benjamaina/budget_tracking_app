from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum


class Donor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="donors", db_index=True)
    name = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.phone_number}"


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events", db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    venue = models.CharField(max_length=55, db_index=True, blank=True, null=True)
    description = models.TextField(blank=True)
    total_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_index=True,
        help_text="Total budget allocated for the event"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    date = models.DateField(default=timezone.now, db_index=True)
    time = models.TimeField(default=timezone.now)

    def total_pledged(self):
        if not self.pk:
            return 0
        return sum(p.amount_pledged for p in self.pledges.all())

    def total_received(self):
        if not self.pk:
            return 0
        return sum(p.total_paid() for p in self.pledges.all())

    def percentage_covered(self):
        total = self.total_pledged()
        return round((self.total_received() / total) * 100, 2) if total else 0

    def outstanding_balance(self):
        return self.total_pledged() - self.total_received()

    @property
    def is_funded(self):
        return self.total_budget <= self.total_received()


    def clean(self):
        if self.date < timezone.now().date():
            raise ValidationError("Event date cannot be in the past.")
        if not self.name:
            raise ValidationError("Event name cannot be empty.")
        if self.total_budget < 0:
            raise ValidationError("Total budget cannot be negative.")

    def budget_summary(self):
        if not self.pk:
            return {
                "total_budget": 0,
                "total_allocated": 0,
                "total_spent": 0
            }
        return {
            "total_budget": sum(item.estimated_budget for item in self.budget_items.all()),
            "total_allocated": sum(task.allocated_amount for item in self.budget_items.all() for task in item.tasks.all()),
            "total_spent": sum(task.amount_paid for item in self.budget_items.all() for task in item.tasks.all()),
        }

    @property
    def venue_display(self):
        return self.venue if self.venue else "Venue not specified"

    def __str__(self):
        return f"{self.name} - {self.date}"

    class Meta:
        ordering = ['-date']


class BudgetItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budget_items", db_index=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="budget_items", db_index=True)
    category = models.CharField(max_length=255, db_index=True)
    estimated_budget = models.DecimalField(max_digits=12, decimal_places=2)
    is_funded = models.BooleanField(default=False)

    def clean(self):
        if self.estimated_budget < 0:
            raise ValidationError("Estimated budget cannot be negative.")
        if not self.category:
            raise ValidationError("Category cannot be empty.")

def save(self, *args, **kwargs):
    is_new = self.pk is None  

    super().save(*args, **kwargs)  

    if not is_new:  
        self.is_funded = self.estimated_budget <= sum(
            task.amount_paid for task in self.tasks.all()
        )
        super().save(update_fields=["is_funded"])

    def __str__(self):
        return f"{self.category} - KES {self.estimated_budget}"


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks", db_index=True)
    budget_item = models.ForeignKey(BudgetItem, on_delete=models.CASCADE, related_name="tasks", db_index=True)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField(db_index=True)
    completed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.completed = self.amount_paid >= self.allocated_amount
        super().save(*args, **kwargs)

    @property
    def balance(self):
        return max(self.allocated_amount - self.amount_paid, 0)

    def is_overdue(self):
        return self.due_date < timezone.now().date() and not self.completed

    def is_due_today(self):
        return self.due_date == timezone.now().date() and not self.completed

    def __str__(self):
        return f"{self.title} - Due: {self.due_date}"


class Pledge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pledges", db_index=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="pledges", db_index=True)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name="pledges", db_index=True)
    amount_pledged = models.DecimalField(max_digits=10, decimal_places=2)
    is_fulfilled = models.BooleanField(default=False)

    def total_paid(self):
        if not self.pk:
            return 0
        total_mpesa = sum(p.amount for p in self.payments.all())
        total_manual = sum(p.amount for p in self.manual_payments.all())
        return total_mpesa + total_manual

    def balance(self):
        if not self.pk:
            return 0
        return max(self.amount_pledged - self.total_paid(), 0)

    def payment_breakdown(self):
        return {
            "Mpesa": sum(p.amount for p in self.payments.all()),
            "Manual": sum(p.amount for p in self.manual_payments.all())
        }

    def save(self, *args, **kwargs):
        self.is_fulfilled = self.total_paid() >= self.amount_pledged
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.donor.name} pledged KES {self.amount_pledged}"


class MpesaPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mpesa_payments", db_index=True)
    pledge = models.ForeignKey(Pledge, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', db_index=True)
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True, related_name='mpesa_payments', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Payment amount must be positive.")

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and self.pledge:
            self.pledge.save()

    def __str__(self):
        return f"{self.transaction_id} - KES {self.amount}"


class ManualPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="manual_payments", db_index=True)
    pledge = models.ForeignKey(Pledge, on_delete=models.SET_NULL, null=True, blank=True, related_name='manual_payments', db_index=True)
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True, related_name='manual_payments', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now, db_index=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Payment amount must be positive.")

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and self.pledge:
            self.pledge.save()

    def __str__(self):
        return f"Manual Payment - KES {self.amount} on {self.date}"
