from rest_framework import serializers
from .models import Event, BudgetItem, Pledge, MpesaPayment, ManualPayment, Donor
from django.contrib.auth.models import User

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "description", "date", "time", "created_by"]

    def create(self, validated_data):
        # Automatically set the created_by field to the current user
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        return super().create(validated_data)


class BudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetItem
        fields = ['id', 'event', 'category', 'estimated_cost', 'is_paid']

class PledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pledge
        fields = ['id', 'event', 'name', 'phone_number', 'amount_pledged', 'amount_paid', 'is_fulfilled']

class MpesaPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaPayment
        fields = ['phone_number', 'amount', 'transaction_id', 'timestamp', 'name']
        read_only_fields = ['timestamp', 'transaction_id', 'phone_number', 'name']

    def create(self, validated_data):
        phone = validated_data.get('phone_number')
        pledge = Pledge.objects.filter(phone_number=phone).order_by('-id').first()
        validated_data['pledge'] = pledge
        return super().create(validated_data)

class ManualPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaPayment
        fields = ['phone_number', 'amount', 'transaction_id', 'timestamp', 'name']
        read_only_fields = ['timestamp', 'transaction_id', 'phone_number', 'name']

    def create(self, validated_data):
        phone = validated_data.get('phone_number')
        pledge = Pledge.objects.filter(phone_number=phone).order_by('-id').first()
        validated_data['pledge'] = pledge
        return super().create(validated_data)