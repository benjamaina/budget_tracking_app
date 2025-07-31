from rest_framework import serializers
from .models import Event, BudgetItem, Pledge, MpesaPayment, ManualPayment, Task, MpesaInfo, VendorPayment, ServiceProvider
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
    class Meta:
        model = Pledge
        fields = ['id', 'event',  'amount_pledged', 'is_fulfilled', 'name', 'phone_number']
        read_only_fields = ['id']
        
    def validate(self, attrs):
        if attrs.get('amount_pledged') <= 0:
            raise serializers.ValidationError("Amount pledged must be greater than zero.")
        return attrs
        
        
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data['user'] = user


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
    
class VendorPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPayment
        fields = ['id', 'vendor', 'amount', 'date', 'description']
        read_only_fields = ['id']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)
    
class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = ['id', 'name', 'contact_info']
        read_only_fields = ['id']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


