import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.permissions import IsAuthenticated
from booking.models import Booking
from .models import Payment
from .serializers import PaymentSerializer


class StartPaymentView(APIView):
    """
    Starts Razorpay payment for a booking.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'payment_page.html'
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        # Example: ₹100 per seat
        seat_price = 1  
        total_amount = booking.seats_booked * seat_price * 100  # convert to paise

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": total_amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        payment = Payment.objects.create(
            user=request.user,
            booking=booking,
            razorpay_order_id=razorpay_order["id"],
            amount=total_amount / 100,
        )

        serializer = PaymentSerializer(payment)

        context = {
            "serializer": serializer,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "order_id": razorpay_order["id"],
            "amount": total_amount,
            "booking": booking,
        }
        return Response(context)


class PaymentSuccessView(APIView):
    """
    Handles Razorpay payment success callback.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'payment_success.html'

    def post(self, request):
        data = request.data
        payment = get_object_or_404(Payment, razorpay_order_id=data.get('razorpay_order_id'))

        payment.razorpay_payment_id = data.get('razorpay_payment_id')
        payment.razorpay_signature = data.get('razorpay_signature')
        payment.paid = True
        payment.save()

        messages.success(request, "Payment successful! Your booking is confirmed.")
        return Response({"payment": payment})
