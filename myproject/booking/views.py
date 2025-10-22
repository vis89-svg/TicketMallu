from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth import logout  
from myapp.models import Event
from .models import Booking, Seat
from .serializers import BookingSerializer

# ----------------------------
# Registration
# ----------------------------
class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        messages.success(self.request, "Account created! Please login.")
        return super().form_valid(form)

# ----------------------------
# Booking List
# ----------------------------
class BookingListView(LoginRequiredMixin, APIView):
    login_url = '/login/'
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'booking_list.html'

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
        return Response({'bookings': bookings})

# ----------------------------
# Seat Selector / Booking
# ----------------------------
class SeatSelectorView(LoginRequiredMixin, APIView):
    login_url = '/login/'
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'seat_selector.html'

    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        booked_seats = Seat.objects.filter(booking__event=event).values_list('seat_number', flat=True)
        seats = list(range(1, event.total_seats + 1))
        return Response({'event': event, 'seats': seats, 'booked_seats': booked_seats})

    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        selected_seats = request.POST.getlist('seats')  # list of selected seat numbers

        if not selected_seats:
            messages.error(request, "Select at least one seat.")
            return redirect('seat-selector', event_id=event.id)

        booked_seats = Seat.objects.filter(booking__event=event).values_list('seat_number', flat=True)
        for seat in selected_seats:
            if int(seat) in booked_seats:
                messages.error(request, f"Seat {seat} is already booked.")
                return redirect('seat-selector', event_id=event.id)

        # Create booking and seats
        booking = Booking.objects.create(user=request.user, event=event, seats_booked=len(selected_seats))
        for seat in selected_seats:
            Seat.objects.create(booking=booking, seat_number=int(seat))

        event.available_seats -= len(selected_seats)
        event.save()

        messages.success(request, f"Successfully booked seats: {', '.join(selected_seats)}")

        # ✅ Redirect to Razorpay payment page
        return redirect('start-payment', booking_id=booking.id)

def logout_view(request):
    logout(request)  # logs out the user
    return render(request, 'logout.html')  # renders your logout page