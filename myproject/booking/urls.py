from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # User
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
  
    # Booking
    path('booking_list/', views.BookingListView.as_view(), name='booking-list'),
    path('seat-selector/<int:event_id>/', views.SeatSelectorView.as_view(), name='seat-selector'),
]
