from rest_framework import serializers
from .models import Event, BudgetItem, Pledge, MpesaPayment, ManualPayment, Donor, Task
from django.contrib.auth.models import User

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "description", "date", "time", "created_by", "venue", "total_budget"]
        read_only_fields = ["id", "created_by"]

        
    def create(self, validated_data):
        # Automatically set the created_by field to the current user
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        return super().create(validated_data)


class BudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetItem
        fields = ['id', 'event', 'category', 'estimated_budget', 'is_funded']

class PledgeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='donor.name')
    phone_number = serializers.CharField(source='donor.phone_number')
    class Meta:
        model = Pledge
        fields = ['id', 'event',  'amount_pledged', 'is_fulfilled', 'name', 'phone_number']
        read_only_fields = ['id']


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

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'allocated_amount', 'amount_paid', 'due_date', 'completed']
        read_only_fields = ['id']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)