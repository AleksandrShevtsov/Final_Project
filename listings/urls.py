from django.urls import path
from .views import (ListingView, ListingDetailView, BookingListCreateView,
                    ReviewListView, ReviewDetailView, BookingDetailView)

urlpatterns = [
    path('', ListingView.as_view(), name='listings'),
    path('<int:pk>/', ListingDetailView.as_view(), name='listing_detail'),
    path('<int:listing_id>/bookings/', BookingListCreateView.as_view(), name='bookings'),
    path('<int:listing_id>/bookings/<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('<int:listing_id>/reviews/', ReviewListView.as_view(), name='review_list'),
    path('<int:listing_id>/reviews/<int:pk>/', ReviewDetailView.as_view(), name='review_detail'),

    ]
