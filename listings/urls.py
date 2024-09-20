from django.urls import path
from .views import ListingView, ListingDetailView, BookingView, ReviewView

urlpatterns = [
    path('', ListingView.as_view(), name='listings'),
    path('<int:pk>/', ListingDetailView.as_view(), name='listing_detail'),
    path('bookings/', BookingView.as_view(), name='bookings'),
    path('<int:listing_id>/reviews/', ReviewView.as_view(), name='reviews'),
    ]
