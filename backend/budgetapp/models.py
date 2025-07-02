from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Donor: centralizes people info to avoid duplicate names/numbers
class Donor(models.Model):
    name = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.phone_number}"


# Event someone is organizing
class Event(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    date = models.DateField(default=timezone.now, db_index=True)
    time = models.TimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.date}"


# Budget item/category like Food, Venue, Decor etc.
class BudgetItem(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="budget_items", db_index=True)
    category = models.CharField(max_length=255, db_index=True)
    estimated_budget = models.DecimalField(max_digits=12, decimal_places=2)
    is_funded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category} - KES {self.estimated_budget}"


# Task under a budget item
class Task(models.Model):
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

    def update_amount_paid(self, amount):
        self.amount_paid += amount
        self.save()

    def __str__(self):
        return f"{self.title} - Due: {self.due_date}"


# Pledges for an event
class Pledge(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="pledges", db_index=True)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name="pledges", db_index=True)
    amount_pledged = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_fulfilled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.is_fulfilled = self.amount_paid >= self.amount_pledged
        super().save(*args, **kwargs)

    @property
    def balance(self):
        return max(self.amount_pledged - self.amount_paid, 0)

    def update_amount_paid(self, amount):
        self.amount_paid += amount
        self.save()

    def __str__(self):
        return f"{self.donor.name} pledged {self.amount_pledged}"


# M-Pesa Payment linked to a pledge
class MpesaPayment(models.Model):
    pledge = models.ForeignKey(Pledge, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', db_index=True)
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True, related_name='mpesa_payments', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pledge:
            self.pledge.amount_paid += self.amount
            self.pledge.is_fulfilled = self.pledge.amount_paid >= self.pledge.amount_pledged
            self.pledge.save()

    def __str__(self):
        return f"{self.transaction_id} - KES {self.amount}"


# Manual payment not through M-Pesa
class ManualPayment(models.Model):
    pledge = models.ForeignKey(Pledge, on_delete=models.SET_NULL, null=True, blank=True, related_name='manual_payments', db_index=True)
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True, related_name='manual_payments', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now, db_index=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pledge:
            self.pledge.amount_paid += self.amount
            self.pledge.is_fulfilled = self.pledge.amount_paid >= self.pledge.amount_pledged
            self.pledge.save()

    def __str__(self):
        return f"Manual Payment - KES {self.amount} on {self.date}"
