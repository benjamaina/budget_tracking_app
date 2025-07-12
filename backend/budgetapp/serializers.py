from rest_framework import serializers
from .models import Event, BudgetItem, Pledge, MpesaPayment, ManualPayment, Donor, Task, MpesaInfo
from django.utils import timezone
from django.contrib.auth.models import User

class MpesaInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaInfo
        fields = ['id', 'paybill_number', 'till_number', 'account_name',  'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "description", "date", "time", "created_by", "venue", "total_budget", 'user']
        read_only_fields = ["id", "created_by", "user"]


    def create(self, validated_data):
        # Automatically set the created_by field to the current user
        request = self.context.get('request')
        validated_data['user'] = request.user
        validated_data['created_by'] = self.context['request'].user
        # Ensure the user is set to the current user
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
        
    def validate(self, attrs):
        if attrs.get('amount_pledged') <= 0:
            raise serializers.ValidationError("Amount pledged must be greater than zero.")
        return attrs
        
        donor_data = data.get('donor', {})
        if not donor_data.get('phone_number') and not donor_data.get('name'):
            raise serializers.ValidationError("Donor phone number and name are required.")
        return data
        
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data['user'] = user

        donor_data = validated_data.pop('donor', {})
        donor, created = Donor.objects.get_or_create(
            user=user,
            phone_number=donor_data.get('phone_number'),
            name=donor_data.get('name'),
        )
        validated_data['donor'] = donor
        return super().create(validated_data)

# class MpesaPaymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MpesaPayment
#         fields = ['phone_number', 'amount', 'transaction_id', 'timestamp', 'name']
#         read_only_fields = ['timestamp', 'transaction_id', 'phone_number', 'name']

#     def create(self, validated_data):
#         phone = validated_data.get('phone_number')
#         pledge = Pledge.objects.filter(doner_phone_number=phone).order_by('-id').first()
#         validated_data['pledge'] = pledge
#         return super().create(validated_data)

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