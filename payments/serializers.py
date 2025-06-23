# payments/serializers.py
from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'method', 'amount', 'status',
            'transaction_id', 'phone_number', 'reference',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'transaction_id', 'reference']