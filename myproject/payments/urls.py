from django.urls import path
from .views import StartPaymentView, PaymentSuccessView

urlpatterns = [
    path('start/<int:booking_id>/', StartPaymentView.as_view(), name='start-payment'),
    path('success/', PaymentSuccessView.as_view(), name='payment-success'),
]
