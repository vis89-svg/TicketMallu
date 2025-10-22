from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'booking',
            'razorpay_order_id',
            'razorpay_payment_id',
            'razorpay_signature',
            'amount',
            'paid',
            'created_at',
        ]
        read_only_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'paid', 'created_at']
