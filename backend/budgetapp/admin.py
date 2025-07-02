from django.contrib import admin
from .models import Event, BudgetItem, Pledge, MpesaPayment, ManualPayment, Donor
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import ModelAdmin, register


admin.site.site_header = "Budget Management Admin"
admin.site.site_title = "Budget Management Admin Portal"
admin.site.index_title = "Welcome to the Budget Management Admin Portal"


@register(Event)
class EventAdmin(ModelAdmin):
    list_display = ('name', 'date', 'created_by')
    search_fields = ('name', 'description')
    list_filter = ('date', 'created_by')
    ordering = ('-date',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'created_by', 'date', 'time')
        }),
    )


@register(BudgetItem)
class BudgetItemAdmin(ModelAdmin):
    list_display = ('event', 'category', 'estimated_budget', 'is_funded')
    search_fields = ('category',)
    list_filter = ('event', 'is_funded')
    ordering = ('-estimated_budget',)
    fieldsets = (
        (None, {
            'fields': ('event', 'category', 'estimated_budget', 'is_funded')
        }),
    )


@register(Pledge)
class PledgeAdmin(ModelAdmin):
    list_display = ('event', 'donor', 'amount_pledged', 'is_fulfilled')
    search_fields = ('donor__name', 'event__name')
    list_filter = ('is_fulfilled', 'event')
    ordering = ('-amount_pledged',)
    fieldsets = (
        (None, {
            'fields': ('event', 'donor', 'amount_pledged', 'amount_paid', 'is_fulfilled')
        }),
    )


@register(MpesaPayment)
class MpesaPaymentAdmin(ModelAdmin):
    list_display = ('transaction_id', 'amount', 'get_phone_number', 'is_linked', 'timestamp')
    search_fields = ('transaction_id', 'donor__phone_number')
    readonly_fields = ('timestamp',)
    list_filter = ('donor',)
    ordering = ('-timestamp',)
    fieldsets = (
        (None, {
            'fields': ('transaction_id', 'amount', 'donor', 'timestamp')
        }),
    )

    def get_phone_number(self, obj):
        return obj.donor.phone_number if obj.donor else "—"
    get_phone_number.short_description = 'Phone Number'

    def is_linked(self, obj):
        return bool(obj.pledge)
    is_linked.boolean = True
    is_linked.short_description = "Linked to Pledge"


@register(ManualPayment)
class ManualPaymentAdmin(ModelAdmin):
    list_display = ('pledge', 'amount', 'date')
    search_fields = ('pledge__donor__name', 'pledge__event__name')
    list_filter = ('date',)
    ordering = ('-date',)
    fieldsets = (
        (None, {
            'fields': ('pledge', 'donor', 'amount', 'date')
        }),
    )
