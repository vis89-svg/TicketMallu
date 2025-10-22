from rest_framework import serializers
from .models import Booking, Seat

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['seat_number']

class BookingSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)
    event_image = serializers.ImageField(source='event.image', read_only=True)  # new field for the event image

    class Meta:
        model = Booking
        fields = ['id', 'user', 'event', 'event_image', 'seats_booked', 'booking_date', 'seats']
        read_only_fields = ['user', 'booking_date', 'seats', 'event_image']
