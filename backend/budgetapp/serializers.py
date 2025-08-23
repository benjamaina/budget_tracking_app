from rest_framework import serializers
from .models import (
    Event, BudgetItem, Pledge, MpesaPayment, 
    ManualPayment, Task, MpesaInfo, VendorPayment, ServiceProvider, UserSettings
)
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['id','preferred_currency', 'mpesa_paybill_number', 'mpesa_till_number',
                  'mpesa_account_name', 'user', 'mpesa_phone_number',
                  'preferred_currency', 'notifications_enabled ']
        read_only_fields = ['id', 'user', 'notifications_enabled ']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

# Mpesa Info
class MpesaInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaInfo
        fields = ['id', 'paybill_number', 'till_number', 'account_name', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Event
class EventSerializer(serializers.ModelSerializer):
    total_received = serializers.SerializerMethodField()
    total_pledged = serializers.SerializerMethodField()
    percentage_covered = serializers.SerializerMethodField()
    outstanding_balance = serializers.SerializerMethodField()
    overpaid_amount = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id", "name", "description", "venue", "total_budget", "event_date",
            "user", "is_funded", "total_received", "total_pledged",
            "percentage_covered", "outstanding_balance", "overpaid_amount"
        ]
        read_only_fields = [
            "id", "user", "is_funded",
            "total_received", "total_pledged", "percentage_covered", 
            "outstanding_balance", "overpaid_amount"
        ]

    def get_total_received(self, obj):
        return obj.total_received()

    def get_total_pledged(self, obj):
        return obj.total_pledged()

    def get_percentage_covered(self, obj):
        return obj.percentage_covered()

    def get_outstanding_balance(self, obj):
        return obj.outstanding_balance()

    def get_overpaid_amount(self, obj):
        return obj.overpaid_amount()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Budget Item
class BudgetItemSerializer(serializers.ModelSerializer):
    total_vendor_payments = serializers.SerializerMethodField()
    remaining_budget = serializers.SerializerMethodField()
    is_fully_paid = serializers.SerializerMethodField()

    class Meta:
        model = BudgetItem
        fields = [
            'id', 'event', 'category', 'estimated_budget', 'is_funded',
            'total_vendor_payments', 'remaining_budget', 'is_fully_paid'
        ]
        extra_kwargs = {
            'event': {'required': True}
        }
        read_only_fields = ['id', 'total_vendor_payments', 'remaining_budget', 'is_fully_paid']

    def get_total_vendor_payments(self, obj):
        return obj.total_vendor_payments

    def get_remaining_budget(self, obj):
        return obj.remaining_budget

    def get_is_fully_paid(self, obj):
        return obj.is_fully_paid

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Pledge
class PledgeSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Pledge
        fields = [
            'id', 'event', 'amount_pledged', 'is_fulfilled',
            'name', 'phone_number', 'user', 'total_paid', 'balance'
        ]
        read_only_fields = ['id', 'is_fulfilled', 'user', 'total_paid', 'balance']

    def get_balance(self, obj):
        return obj.balance()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


    def validate(self, data):
        event = data.get('event')
        amount_pledged = data.get('amount_pledged')

        # Sum of pledges for this event excluding current pledge if updating
        total_pledged = Pledge.objects.filter(event=event).aggregate(
            total=Sum('amount_pledged')
        )['total'] or 0

        # If updating, subtract existing pledge amount to avoid double counting
        if self.instance:
            total_pledged -= self.instance.amount_pledged

        if amount_pledged + total_pledged > event.total_budget:
            raise serializers.ValidationError("Pledge amount exceeds event's total budget.")
        
        if amount_pledged <= 0:
            raise serializers.ValidationError("Amount pledged must be greater than zero.")
        return data

# Mpesa Payment
class MpesaPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaPayment
        fields = ['id', 'event', 'pledge', 'amount', 'transaction_id', 'timestamp', 'user']
        read_only_fields = ['id', 'timestamp', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Manual Payment
class ManualPaymentSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = ManualPayment
        fields = ['id', 'event', 'pledge', 'amount', 'date', 'user', 'phone_number', 'name']
        read_only_fields = ['id', 'date', 'user', 'phone_number', 'name']

    def get_phone_number(self, obj):
        return obj.pledge.phone_number if obj.pledge else None

    def get_name(self, obj):
        return obj.pledge.name if obj.pledge else None

    def create(self, validated_data):
        # show data being saved by the user
        print(f"Saving ManualPayment: {validated_data} by user {self.context['request'].user}")
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Task
class TaskSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'budget_item', 'title', 'description', 'allocated_amount', 'amount_paid', 'balance', 'user']
        read_only_fields = ['id', 'user', 'balance']

    def get_balance(self, obj):
        return obj.balance

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Vendor Payment
class VendorPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPayment
        fields = [
            'id', 'budget_item', 'service_provider', 'payment_method',
            'transaction_code', 'amount', 'confirmed', 'date_paid', 'user'
        ]
        read_only_fields = ['id', 'date_paid', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Service Provider
class ServiceProviderSerializer(serializers.ModelSerializer):
    total_received = serializers.SerializerMethodField()
    balance_due = serializers.SerializerMethodField()

    class Meta:
        model = ServiceProvider
        fields = [
            'id', 'budget_item', 'service_type', 'name', 'phone_number',
            'email', 'amount_charged', 'total_received', 'balance_due', 'user'
        ]
        read_only_fields = ['id', 'total_received', 'balance_due', 'user']

    def get_total_received(self, obj):
        return obj.total_received

    def get_balance_due(self, obj):
        return obj.balance_due

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# User Registration
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    
    def validate_new_password(self, value):
        user = self.context['request'].user
        if  user.check_password(value):
            raise serializers.ValidationError("New password cannot be the same as the old password")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
