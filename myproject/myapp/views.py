from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from django.db.models import Q, Count
from .models import Event
from .serializers import EventSerializer
from booking.models import Seat
from django.contrib.auth import logout

class EventListView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'event_list.html'

    def get(self, request):
        query = request.GET.get('q', '')
        date_filter = request.GET.get('date', '')
        location_filter = request.GET.get('location', '')

        events = Event.objects.all().order_by('date')

        if query:
            events = events.filter(Q(title__icontains=query) | Q(location__icontains=query))

        if date_filter:
            events = events.filter(date__date=date_filter)

        if location_filter:
            events = events.filter(location__iexact=location_filter)

        # ✅ Calculate available_seats dynamically for each event
        for event in events:
            booked_count = Seat.objects.filter(booking__event=event).count()
            event.available_seats = event.total_seats - booked_count

       
        MINIMUM_BOOKINGS = 5  # BOOKING LOGIC 1 -- WORING MODE , mimum to percentage ratio used here 
        MINIMUM_BOOKING_PERCENTAGE = 20  
        
        all_events_with_bookings = Event.objects.annotate(
            booking_count=Count('booking')
        ).filter(booking_count__gte=MINIMUM_BOOKINGS)
        
        
        if location_filter:
            all_events_with_bookings = all_events_with_bookings.filter(location__iexact=location_filter)
        
        trending_events = []
        for event in all_events_with_bookings:
            booked_count = Seat.objects.filter(booking__event=event).count()
            available = event.total_seats - booked_count
            booking_percentage = (booked_count / event.total_seats) * 100
            
           
            if available > 0 and booking_percentage >= MINIMUM_BOOKING_PERCENTAGE:
                event.available_seats = available
                event.booking_count = booked_count
                event.booking_percentage = booking_percentage
                trending_events.append(event)
        
        # Booking logic percnetgae , 2 nd solution WORKING . 
        trending_events = sorted(
            trending_events, 
            key=lambda e: (e.booking_percentage, e.booking_count), 
            reverse=True
        )[:6]

       
        categorized_events = {}
        for choice_value, choice_label in Event.CATEGORY_CHOICES:
            category_events = events.filter(category=choice_value)
            if category_events.exists():  # Only show categories that have events
                categorized_events[choice_label] = category_events

        return Response({
            'categorized_events': categorized_events,
            'trending_events': trending_events,
            'query': query,
            'date_filter': date_filter
        })


class EventDetailView(APIView):
   
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'event_detail.html'

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        booked_count = Seat.objects.filter(booking__event=event).count()
        event.available_seats = event.total_seats - booked_count
        return Response({'event': event})


class EventCreateView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'event_form.html'

    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, "You are not authorized to create events.")
            return redirect('event-list')

        serializer = EventSerializer()
        return Response({'serializer': serializer})

    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, "You are not authorized to create events.")
            return redirect('event-list')

        data = request.POST.copy()
        data.update(request.FILES)
        
        serializer = EventSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Event created successfully!")
            return redirect('event-list')
        return Response({'serializer': serializer})

#superuser section : EDIT DELETE APPLICATION - admin , 12345 PASSWORD 
class EventUpdateView(APIView): 
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'event_form.html'

    def get(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, "You are not authorized to edit events.")
            return redirect('event-list')

        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event)
        return Response({'serializer': serializer, 'event': event})

    def post(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, "You are not authorized to edit events.")
            return redirect('event-list')

        event = get_object_or_404(Event, pk=pk)
        
        
        data = request.POST.copy()
        data.update(request.FILES)
        
        serializer = EventSerializer(event, data=data)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Event updated successfully!")
            return redirect('event-detail', pk=pk)
        return Response({'serializer': serializer, 'event': event})


class EventDeleteView(APIView):
  
    def post(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, "You are not authorized to delete events.")
            return redirect('event-list')

        event = get_object_or_404(Event, pk=pk)
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('event-list')