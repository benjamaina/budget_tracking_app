from django.contrib import admin
from .models import (Event, BudgetItem, Pledge, MpesaPayment, ManualPayment, 
                     MpesaInfo, Task, VendorPayment, ServiceProvider)
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User




@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('name',  'venue', 'event_date','total_budget', 'total_pledged', 'total_received', 'percentage_covered', 'outstanding_balance', 'is_funded')
    readonly_fields = ('created_on',)
    search_fields = ('name', 'venue', 'user__username')
    list_filter = ('event_date', 'user')

    def total_pledged(self, obj):
        return obj.total_pledged()
    total_pledged.short_description = _('Total Pledged')

    def total_received(self, obj):
        return obj.total_received()
    total_received.short_description = _('Total Received')

    def percentage_covered(self, obj):
        return obj.percentage_covered()
    percentage_covered.short_description = _('Percentage Covered')

    def outstanding_balance(self, obj):
        return obj.outstanding_balance()
    outstanding_balance.short_description = _('Outstanding Balance')

    def save_model(self, request, obj, form, change):
        if not change or not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)
    

@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    # exclude = ('user',)
    list_display = ('event', 'category', 'estimated_budget', 'is_funded')
    search_fields = ('event__name', 'category')
    list_filter = ('is_funded',)


    def total_vendor_payments(self, obj):
        return obj.total_vendor_payments
    total_vendor_payments.short_description = _('Total Vendor Payments')

    def remaining_budget(self, obj):
        return obj.remaining_budget
    remaining_budget.short_description = _('Remaining Budget')

    def is_fully_paid(self, obj):
        return obj.is_fully_paid
    is_fully_paid.short_description = _('Is Fully Paid')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not change or not obj.user_id:
            obj.user = request.user
        print(f"Saving: {obj} by user {request.user}") 
        super().save_model(request, obj, form, change)
        print(f"Saved: {obj} by user {request.user}") 




@admin.register(Pledge)
class PledgeAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('event', 'name', 'phone_number', 'amount_pledged', 'is_fulfilled', 'total_paid')
    search_fields = ('event__name', 'name', 'phone_number')
    readonly_fields = ('balance','total_paid', 'is_fulfilled',)
    list_filter = ('is_fulfilled',)

    def balance(self, obj):
        return obj.balance()
    balance.short_description = _('Balance')


    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('budget_item', 'title', 'description','allocated_amount', 'amount_paid')
    search_fields = ('budget_item__category', 'title')
    list_filter = ('budget_item__category',)



    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(ManualPayment)
class ManualPaymentAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('pledge', 'amount',  'date')
    search_fields = ('event__name',)
    readonly_fields = ('date',)
    list_filter = ('date',)


    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(MpesaPayment)
class MpesaPaymentAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('pledge', 'amount', 'transaction_id', 'timestamp')
    search_fields = ('event__name',  'transaction_id')
    list_filter = ('timestamp',)

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(VendorPayment)
class VendorPaymentAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('budget_item', 'service_provider', 'amount', 'payment_method', 'date_paid', 'confirmed')
    search_fields = ('budget_item__category', 'service_provider__name')
    list_filter = ('payment_method', 'date_paid', 'confirmed')
    readonly_fields = ('date_paid',)
    
    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def amount(self, obj):
        return obj.budget_item.estimated_budget
    amount.short_description = _('Amount')


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('budget_item','name', 'phone_number', 'email', 'amount_charged', 'service_type')
    search_fields = ('name', 'phone_number', 'email')
    list_filter = ('name',)

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)


    def total_received(self, obj):
        return obj.total_received
    total_received.short_description = _('Total Received')

    def balance_due(self, obj):
        return obj.balance_due
    balance_due.short_description = _('Balance Due')
