from django.db import models
from django.contrib.auth.models import User
from myapp.models import Event

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    seats_booked = models.PositiveIntegerField()
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.seats_booked} seats)"

class Seat(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name='seats')
    seat_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('booking', 'seat_number')  # Prevent same seat being booked twice

    def __str__(self):
        return f"{self.booking.event.title} Seat {self.seat_number} ({self.booking.user.username})"
