from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
import logging
from .models import (Event, BudgetItem, Pledge, MpesaPayment, ManualPayment, 
                     MpesaInfo, Task, VendorPayment, ServiceProvider, UserSettings)
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(user=instance)



@receiver([post_save, post_delete], sender=MpesaPayment)
@receiver([post_save, post_delete], sender=ManualPayment)
def update_event_funding_status(sender, instance, **kwargs):
    event_id = getattr(instance, 'event_id', None)
    if event_id:
        try:
            event = Event.objects.filter(id=event_id).first()
            if event:
             event.update_funding_status()
        except Exception as e:
            logging.error(f"Error updating funding status for event {event_id}: {e}")



@receiver([post_save, post_delete], sender=VendorPayment)
def update_budget_item_funding_status(sender, instance, **kwargs):
    budget_item_id = getattr(instance, 'budget_item_id', None)
    if budget_item_id:
        try:
            from budgetapp.models import BudgetItem  # avoid circular import if needed
            item = BudgetItem.objects.filter(pk=budget_item_id).first()
            if item:
                item.update_funding_status()
        except Exception as e:
            logging.error(f"Error updating funding status for budget item {budget_item_id}: {e}")




@receiver([post_save, post_delete], sender=MpesaPayment)
@receiver([post_save, post_delete], sender=ManualPayment)
def update_pledge_payment_status(sender, instance, **kwargs):
    # Defensive: ensure instance still has a pledge
    pledge = getattr(instance, 'pledge', None)
    if pledge is None:
        return  # nothing to update

    try:
        pledge.update_payment_status()
    except Exception as e:
        logging.error(f"Error updating payment status for pledge {getattr(pledge, 'id', 'unknown')}: {e}")


@receiver(post_save, sender=ManualPayment)
def update_pledge_on_manual_payment(sender, instance, created, **kwargs):
    try:
        if instance.pledge:
            instance.pledge.update_payment_status()
    except Exception as e:
        logging.error(f"Error updating pledge from ManualPayment {instance.id}: {e}")


@receiver(post_save, sender=MpesaPayment)
def update_pledge_on_mpesa_payment(sender, instance, created, **kwargs):
    if instance.pledge:
    # Ensure the pledge is updated only if it exists
        try:
            instance.pledge.update_payment_status()
        except Exception as e:
            logging.error(f"Error updating payment status for pledge {instance.pledge.id}: {e}")

