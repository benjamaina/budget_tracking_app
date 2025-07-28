from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db import transaction




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
    event_date = models.DateField(db_index=True)
    created_on = models.DateField(default=timezone.now)
    is_funded = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        is_new = self.pk is None  
        super().save(*args, **kwargs)  

        if not is_new:  
            self.is_funded = self.total_budget <= self.total_received()
            super().save(update_fields=["is_funded"])

    def total_pledged(self):
        if not self.pk:
            return 0
        return sum(p.amount_pledged for p in self.pledges.all())

    def total_received(self):
        if not self.pk:
            return 0
        return sum(p.total_paid for p in self.pledges.all())

    def percentage_covered(self):
        total = self.total_pledged()
        return round((self.total_received() / total) * 100, 2) if total else 0

    def outstanding_balance(self):
        return self.total_pledged() - self.total_received()

    # @property
    # def is_funded(self):
    #     return self.total_budget <= self.total_received()


    def clean(self):
        if self.event_date < timezone.now().date():
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
        return f"{self.name} - {self.event_date}"

    class Meta:
        ordering = ['-event_date']


class BudgetItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budget_items", db_index=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="budget_items", db_index=True)
    category = models.CharField(max_length=255, db_index=True)
    estimated_budget = models.DecimalField(max_digits=12, decimal_places=2)
    is_funded = models.BooleanField(default=False)

    # def auto_assign_user(self):
    #     if not self.user_id:
    #         self.user = self.event.user

    def clean(self):
        # self.auto_assign_user()
        if self.estimated_budget < 0:
            raise ValidationError("Estimated budget cannot be negative.")
        if self.estimated_budget > self.event.total_budget:
            raise ValidationError("Estimated budget cannot exceed the event's total budget.")
        if not self.category:
            raise ValidationError("Category cannot be empty.")

    @property
    def total_paid_to_vendor(self):
        return self.payments.aggregate(total=Sum("amount"))["total"] or 0

    @property
    def is_fully_paid(self):
        return self.total_paid_to_vendor >= self.estimated_cost


    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)
        is_new = self.pk is None
        if not is_new:
            self.is_funded = self.total_paid_to_vendor >= self.estimated_budget
            super().save(update_fields=["is_funded"])

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

    def __str__(self):
        return f"{self.name} - {self.phone_number}"

class VendorPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vendor_payments", db_index=True)
    budget_item = models.ForeignKey(BudgetItem, related_name="payments", on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.CharField(max_length=50, choices=[("mpesa", "Mpesa"), ("bank", "Bank Transfer"), ("cash", "Cash")])
    date_paid = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    confirmed = models.BooleanField(default=False)  
    

    def auto_fill_amount(self):
        if not self.amount:
            self.amount = self.service_provider.amount_charged

    def clean(self):
        if self.payment_method not in ["mpesa", "bank", "cash"]:
            raise ValidationError("Invalid payment method.")
        self.auto_fill_amount()
        paid_total = VendorCashPayment.objects.filter(
            service_provider=self.service_provider
        ).exclude(id=self.id).aggregate(total=Sum("amount"))["total"] or 0

        remaining = self.service_provider.amount_charged - paid_total

        if self.amount:
            if self.amount > remaining:
                raise ValidationError(f"Payment exceeds the remaining balance ({remaining}).")
        else:
            self.amount = remaining
        if self.amount < 0:
            raise ValidationError("Payment amount cannot be negative.")
        
        if self.amount >= self.service_provider.amount_charged:
            self.confirmed = True
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.budget_item.category} - KES {self.amount} via {self.payment_method} on {self.date_paid}"
    
class VendorCashPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vendor_cash_payments", db_index=True)
    budget_item = models.ForeignKey(BudgetItem, related_name="cash_payments", on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="cash_payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Payment amount must be positive.")

    def __str__(self):
        return f"Cash Payment - KES {self.amount} to {self.service_provider.name} on {self.date_paid}"

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks", db_index=True)
    budget_item = models.ForeignKey(BudgetItem, on_delete=models.CASCADE, related_name="tasks", db_index=True)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    

    def save(self, *args, **kwargs):
        self.completed = self.amount_paid >= self.allocated_amount
        super().save(*args, **kwargs)

    @property
    def balance(self):
        return max(self.allocated_amount - self.amount_paid, 0)

    def __str__(self):
        return f"{self.title} - Due: {self.due_date}"


class Pledge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pledges", db_index=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="pledges", db_index=True)
    amount_pledged = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(blank=False, null=False, max_length= 25, db_index=True)
    phone_number = models.IntegerField(db_index=True)
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


    def save(self, *args, **kwargs):
        is_new = self.pk is None  
        super().save(*args, **kwargs)  

        if not is_new:
            if self.total_paid >= self.amount_pledged:
                self.is_fulfilled = True
            else:
                self.is_fulfilled = False
            super().save(update_fields=["is_fulfilled"])


    def __str__(self):
        return f"Pledge for {self.event.name} - KES {self.amount_pledged} by {self.user.username}"


class MpesaPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mpesa_payments", db_index=True)
    pledge = models.ForeignKey(Pledge, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Payment amount must be positive.")

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.pledge:
                self.pledge.update_payment_status()

    def __str__(self):
        return f"{self.transaction_id} - KES {self.amount}"


class ManualPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="manual_payments", db_index=True)
    pledge = models.ForeignKey(Pledge, on_delete=models.SET_NULL, null=True, blank=True, related_name='manual_payments', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now, db_index=True)
    

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Payment amount must be positive.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensures validation is applied

        with transaction.atomic():
            super().save(*args, **kwargs)

            if self.pledge:
                super().save(*args, **kwargs)  
                if self.pledge:
                    self.pledge.update_payment_status()

        


    def __str__(self):
        return f"Manual Payment - KES {self.amount} on {self.date}"


class MpesaInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mpesa_info")
    paybill_number = models.CharField(max_length=20, blank=True, null=True)
    till_number = models.CharField(max_length=20, blank=True, null=True)
    account_name = models.CharField(max_length=50, blank=True, null=True)
    
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



