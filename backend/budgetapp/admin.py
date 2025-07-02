from django.contrib import admin
from .models import Event, BudgetItem, Pledge, MpesaPayment, ManualPayment, Donor
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import ModelAdmin, register, TabularInline


admin.site.site_header = "Budget Management Admin"
admin.site.site_title = "Budget Management Admin Portal"
admin.site.index_title = "Welcome to the Budget Management Admin Portal"


# ============================
# Inline Models
# ============================

class BudgetItemInline(TabularInline):
    model = BudgetItem
    extra = 0
    readonly_fields = ('is_funded',)


class PledgeInline(TabularInline):
    model = Pledge
    extra = 0
    readonly_fields = ('is_fulfilled',)


# ============================
# Event Admin
# ============================

@register(Event)
class EventAdmin(ModelAdmin):
    list_display = (
        'name', 'date','total_budget', 'created_by', 'total_pledged', 'total_received',
        'percentage_covered', 'outstanding_balance', 'venue', "is_funded"
    )
    search_fields = ('name', 'description')
    list_filter = ('date', 'created_by')
    ordering = ('-date',)
    readonly_fields = ('budget_summary_display',)
    inlines = [BudgetItemInline, PledgeInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'venue', 'description', 'total_budget', 'created_by', 'date', 'time')
        }),
        ('Summary', {
            'fields': ('budget_summary_display',),
            'classes': ('collapse',),
        }),
    )

    def total_pledged(self, obj):
        return obj.total_pledged()
    total_pledged.short_description = 'Total Pledged'

    def total_received(self, obj):
        return obj.total_received()
    total_received.short_description = 'Total Received'

    def percentage_covered(self, obj):
        return obj.percentage_covered()
    percentage_covered.short_description = 'Percentage Covered'

    def outstanding_balance(self, obj):
        return obj.outstanding_balance()
    outstanding_balance.short_description = 'Outstanding Balance'

    def budget_summary_display(self, obj):
        summary = obj.budget_summary()
        return (
            f"Total Budget: KES {summary['total_budget']:,}<br>"
            f"Total Allocated: KES {summary['total_allocated']:,}<br>"
            f"Total Spent: KES {summary['total_spent']:,}"
        )
    budget_summary_display.short_description = 'Budget Summary'
    budget_summary_display.allow_tags = True


# ============================
# BudgetItem Admin
# ============================

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


# ============================
# Pledge Admin
# ============================

@register(Pledge)
class PledgeAdmin(ModelAdmin):
    list_display = ('event', 'donor', 'amount_pledged', 'total_paid_display', 'is_fulfilled')
    search_fields = ('donor__name', 'event__name')
    list_filter = ('is_fulfilled', 'event')
    ordering = ('-amount_pledged',)
    readonly_fields = ('total_paid_display',)

    fieldsets = (
        (None, {
            'fields': ('event', 'donor', 'amount_pledged', 'total_paid_display', 'is_fulfilled')
        }),
    )

    def total_paid_display(self, obj):
        return f"KES {obj.total_paid():,}"
    total_paid_display.short_description = "Total Paid"


# ============================
# MpesaPayment Admin
# ============================

@register(MpesaPayment)
class MpesaPaymentAdmin(ModelAdmin):
    list_display = ('transaction_id', 'amount', 'get_phone_number', 'is_linked', 'timestamp')
    search_fields = ('transaction_id', 'donor__phone_number')
    readonly_fields = ('timestamp',)
    list_filter = ('donor',)
    ordering = ('-timestamp',)

    fieldsets = (
        (None, {
            'fields': ('transaction_id', 'amount', 'donor', 'pledge', 'timestamp')
        }),
    )

    def get_phone_number(self, obj):
        return obj.donor.phone_number if obj.donor else "—"
    get_phone_number.short_description = 'Phone Number'

    def is_linked(self, obj):
        return bool(obj.pledge)
    is_linked.boolean = True
    is_linked.short_description = "Linked to Pledge"


# ============================
# ManualPayment Admin
# ============================

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


# ============================
# Donor Admin
# ============================

# @register(Donor)
# class DonorAdmin(ModelAdmin):
#     list_display = ('name', 'phone_number', 'total_pledges', 'total_paid')
#     search_fields = ('name', 'phone_number')
#     ordering = ('name',)

#     def total_pledges(self, obj):
#         return obj.pledges.count()

#     def total_paid(self, obj):
#         return sum(p.total_paid() for p in obj.pledges.all())

#     total_pledges.short_description = "No. of Pledges"
#     total_paid.short_description = "Total Paid (All)"
