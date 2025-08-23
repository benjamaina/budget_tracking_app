from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db import transaction
import logging


logger = logging.getLogger(__name__)

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    preferred_currency = models.CharField(max_length=10, default="KES")
    notifications_enabled = models.BooleanField(default=True)

    # Mpesa settings
    mpesa_paybill_number = models.CharField(max_length=20, blank=True, null=True)
    mpesa_till_number = models.CharField(max_length=20, blank=True, null=True)
    mpesa_account_name = models.CharField(max_length=50, blank=True, null=True)
    mpesa_phone_number = models.CharField(max_length=15, blank=True, null=True, db_index=True)


    def __str__(self):
        return f"Settings for {self.user.username}"


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events", db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    venue = models.CharField(max_length=55, db_index=True, blank=True, null=True)
    description = models.TextField(blank=True)
    total_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_index=True,
        help_text="Total budget allocated for the event"
    )
    event_date = models.DateField(db_index=True)
    created_on = models.DateField(default=timezone.now)
    is_funded = models.BooleanField(default=False)
        

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensures validation is applied
        super().save(*args, **kwargs)  


    def update_funding_status(self):
        self.is_funded = self.total_received() >= self.total_budget
        self.save(update_fields=["is_funded"])


    def total_pledged(self):
        return self.pledges.aggregate(total=models.Sum('amount_pledged'))['total'] or 0

    def total_received(self):
        total_mpesa = self.mpesa_payments.aggregate(total=models.Sum('amount'))['total'] or 0
        total_manual = self.manual_payments.aggregate(total=models.Sum('amount'))['total'] or 0
        return total_mpesa + total_manual
    
    def percentage_covered(self):
        total = self.total_pledged()
        return round((self.total_received() / total) * 100, 2) if total else 0

    def outstanding_balance(self):
        balance = self.total_pledged() - self.total_received()

        return max(balance, 0) 
    
    def overpaid_amount(self):
        excess = self.total_received() - self.total_budget
        return max(excess, 0)


    def clean(self):
        if not self.name:
            raise ValidationError("Event name cannot be empty.")
        if self.total_budget < 0:
            raise ValidationError("Total budget cannot be negative.")

    def budget_summary(self):
        if not self.pk:
            return {'total_budget': 0, 'total_spent': 0}
        
        summary = self.budget_items.aggregate(
            total_budget=Sum('estimated_budget'),
            total_spent=Sum('payments__amount')
        )
        return {
            'total_budget': summary['total_budget'] or 0,
            'total_spent': summary['total_spent'] or 0,
        }

    @property
    def venue_display(self):
        return self.venue if self.venue else "Venue not specified"

    def __str__(self):
        return f"{self.name} - {self.event_date}"

    class Meta:
        ordering = ['-event_date']


class BudgetItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budget_items", db_index=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="budget_items", db_index=True, null=True, blank=True)
    category = models.CharField(max_length=255, db_index=True)
    estimated_budget = models.DecimalField(max_digits=12, decimal_places=2)
    is_funded = models.BooleanField(default=False)

    @property
    def total_vendor_payments(self):
        return self.payments.aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def remaining_budget(self):
        return max(self.estimated_budget- self.total_vendor_payments, 0)


    def clean(self):
        if self.estimated_budget < 0:
            raise ValidationError("Estimated budget cannot be negative.")
        if not self.category:
            raise ValidationError("Category cannot be empty.")

        # Validate total estimated budget does not exceed event's total_budget
        sibling_items = BudgetItem.objects.filter(event=self.event)
        if self.pk:
            sibling_items = sibling_items.exclude(pk=self.pk)

        total_estimated = sibling_items.aggregate(total=Sum('estimated_budget'))['total'] or 0
        combined_total = total_estimated + self.estimated_budget

        if combined_total > self.event.total_budget:
            raise ValidationError(
                f"Total estimated budget for all items ({combined_total}) exceeds event's total budget ({self.event.total_budget})."
            )


    @property
    def is_fully_paid(self):
        return self.total_vendor_payments >= self.estimated_budget

    def update_funding_status(self):
        self.is_funded = self.total_vendor_payments >= self.estimated_budget
        self.save(update_fields=["is_funded"])


    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)
        

    def __str__(self):
        return f"{self.category} - KES {self.estimated_budget}"

class ServiceProvider(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="service_providers", db_index=True)
    budget_item = models.ForeignKey(BudgetItem, on_delete=models.CASCADE, related_name="service_providers", db_index=True)
    service_type = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    phone_number = models.CharField(max_length=15, db_index=True)
    email = models.EmailField(blank=True, null=True, db_index=True)
    amount_charged = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def total_received(self):
        return self.payments.aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def balance_due(self):
        return max(self.amount_charged - self.total_received, 0)

    def clean(self):
        if self.budget_item and self.amount_charged > self.budget_item.estimated_budget:
            raise ValidationError("Amount charged cannot exceed budget item estimated budget.")
        # prevent VendorPayments > BudgetItem.estimated_budget
        if self.amount_charged < 0:
            raise ValidationError("Amount charged cannot be negative.")
        if not self.name:
            raise ValidationError("Service provider name cannot be empty.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} - {self.phone_number}"



class VendorPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vendor_payments", db_index=True)
    budget_item = models.ForeignKey(BudgetItem, related_name="payments", on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.CharField(max_length=50, choices=[("mpesa", "Mpesa"), ("bank", "Bank Transfer"), ("cash", "Cash")])
    transaction_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    date_paid = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    confirmed = models.BooleanField(default=False)  
    

    @property
    def total_paid(self):
        return self.budget_item.total_vendor_payments

    

    def clean(self):
        if not self.service_provider:
            raise ValidationError("Service provider is required.")
        if not self.budget_item:
            raise ValidationError("Budget item is required.")
        if self.amount is None:
            raise ValidationError("Payment amount is required.")
       
        

        # Exclude this instance if updating
        existing_payments = self.budget_item.payments.exclude(pk=self.pk)
        total_already_paid = existing_payments.aggregate(total=models.Sum('amount'))['total'] or 0
        total_after_this_payment = total_already_paid + self.amount

        if total_after_this_payment > self.service_provider.amount_charged:
            raise ValidationError("Total payments would exceed the vendor's amount charged.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.budget_item.category} - KES {self.amount} via {self.payment_method} on {self.date_paid}"
 


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks", db_index=True)
    budget_item = models.ForeignKey(BudgetItem, on_delete=models.CASCADE, related_name="tasks", db_index=True)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)

        
    def clean(self):
        if self.allocated_amount < 0:
            raise ValidationError("Allocated amount cannot be negative.")
        if self.amount_paid < 0:
            raise ValidationError("Amount paid cannot be negative.")
        if self.amount_paid > self.allocated_amount:
            raise ValidationError("Amount paid cannot exceed allocated amount.")
        
        # Validate total allocated for all tasks under this budget item
        sibling_tasks = Task.objects.filter(budget_item=self.budget_item)
        if self.pk:
            sibling_tasks = sibling_tasks.exclude(pk=self.pk)

        total_allocated = sibling_tasks.aggregate(total=Sum('allocated_amount'))['total'] or 0
        combined_total = total_allocated + self.allocated_amount

        if combined_total > self.budget_item.estimated_budget:
            raise ValidationError(
                f"Total allocated amount for tasks ({combined_total}) exceeds budget item estimated budget ({self.budget_item.estimated_budget})."
            )


    def save(self, *args, **kwargs):
        self.full_clean()  # Ensures validation is applied
        super().save(*args, **kwargs)

    @property
    def balance(self):
        return max(self.allocated_amount - self.amount_paid, 0)

    def __str__(self):
        return f"{self.title} - KES {self.allocated_amount} ({self.budget_item.category})"


class Pledge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pledges", db_index=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="pledges", db_index=True, null=True, blank=True)
    amount_pledged = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(blank=False, null=False, max_length= 25, db_index=True)
    phone_number = models.CharField(max_length=15, db_index=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_fulfilled = models.BooleanField(default=False)



    def balance(self):
        if not self.pk:
            return 0
        return max(self.amount_pledged - self.total_paid, 0)

    def payment_breakdown(self):
        return {
            "Mpesa": sum(p.amount for p in self.payments.all()),
            "Manual": sum(p.amount for p in self.manual_payments.all())
        }

    def update_payment_status(self):
        manual_total = self.manual_payments.aggregate(manual=Sum('amount'))['manual'] or 0
        mpesa_total = self.payments.aggregate(mpesa=Sum('amount'))['mpesa'] or 0
        total = manual_total + mpesa_total

        self.total_paid = total
        self.is_fulfilled = total >= self.amount_pledged
        self.save(update_fields=["total_paid", "is_fulfilled"])



    def __str__(self):
        return f"{self.name} - KES {self.amount_pledged} ({self.phone_number})"


class MpesaPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mpesa_payments", db_index=True)
    pledge = models.ForeignKey(Pledge, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', db_index=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="mpesa_payments", db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Payment amount must be positive.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - KES {self.amount}"


class ManualPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="manual_payments", db_index=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="manual_payments", db_index=True, null=True, blank=True)
    pledge = models.ForeignKey(Pledge, on_delete=models.SET_NULL, null=True, blank=True, related_name='manual_payments', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now, db_index=True)
    

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Payment amount must be positive.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensures validation is applied
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Manual Payment - KES {self.amount} on {self.date}"


class MpesaInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mpesa_info")
    paybill_number = models.CharField(max_length=20, blank=True, null=True)
    till_number = models.CharField(max_length=20, blank=True, null=True)
    account_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, db_index=True)
    

    @staticmethod
    def auto_assign_pledge(payment):
        try:
           matched_pledge = Pledge.objects.filter(phone_number=payment.phone_number).order_by('-id').first()
           if matched_pledge:
               payment.pledge = matched_pledge
               payment.save()
        except Pledge.DoesNotExist:
           pass


    def __str__(self):
        return f"M-Pesa Info for {self.user.username}"



