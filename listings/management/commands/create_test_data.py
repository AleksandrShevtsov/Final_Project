# your_app/management/commands/create_test_data.py
from django.core.management.base import BaseCommand
from users.models import User
from listings.models import Listing, Review, Booking
from datetime import date

class Command(BaseCommand):
    help = 'Создает тестовые данные для пользователей, объявлений, отзывов и бронирований.'

    def handle(self, *args, **kwargs):
        landlord = User.objects.create_user(username='landlord', email='landlord@example.com', password='password123', role='landlord')
        tenant = User.objects.create_user(username='tenant', email='tenant@example.com', password='password123')

        listing = Listing.objects.create(
            owner=landlord,
            title="Beautiful Apartment",
            description="A spacious apartment in the city center.",
            location="Berlin, Germany",
            price=1500.00,
            rooms=3,
            type="apartment",
            is_active=True
        )

        review = Review.objects.create(
            listing=listing,
            user=tenant,
            rating=4,
            comment="Great place to stay!"
        )

        booking = Booking.objects.create(
            listing=listing,
            user=tenant,
            start_date=date(2024, 9, 1),
            end_date=date(2024, 9, 10),
            status='confirmed'
        )

        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))
