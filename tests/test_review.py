import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from listings.models import Listing, Booking, Review

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_users():
    tenant = User.objects.create_user(email='tenant@example.com', password='tenantpass', role='tenant')
    landlord = User.objects.create_user(email='landlord@example.com', password='landlordpass', role='landlord')
    return tenant, landlord

@pytest.fixture
def create_listing(create_users):
    _, landlord = create_users
    return Listing.objects.create(owner=landlord, title="Test Listing", location="Test City")

@pytest.fixture
def create_booking(create_users, create_listing):
    tenant, _ = create_users
    return Booking.objects.create(
        listing=create_listing,
        user=tenant,
        start_date='2024-09-20',
        end_date='2024-09-25',
        status='confirmed'
    )

@pytest.fixture
def create_review(create_users, create_listing):
    tenant, _ = create_users
    return Review.objects.create(
        listing=create_listing,
        user=tenant,
        rating=5,
        comment="Great place!"
    )

@pytest.mark.django_db
def test_create_review(api_client, create_booking):
    api_client.force_authenticate(user=create_booking.user)
    response = api_client.post(
        reverse('review_add', args=[create_booking.listing.id]),
        {'listing': create_booking.listing.id, 'rating': 4, 'comment': 'Nice stay!'}
    )
    assert response.status_code == 201
    assert Review.objects.count() == 1

@pytest.mark.django_db
def test_view_reviews(api_client, create_listing, create_review):
    api_client.force_authenticate(user=create_review.user)
    response = api_client.get(reverse('review_list', args=[create_listing.id]))
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
def test_update_review(api_client, create_review):
    api_client.force_authenticate(user=create_review.user)
    response = api_client.patch(
        reverse('review_detail', args=[create_review.id]),
        {'comment': 'Updated review!'}
    )
    assert response.status_code == 200
    create_review.refresh_from_db()
    assert create_review.comment == 'Updated review!'

@pytest.mark.django_db
def test_delete_review(api_client, create_review):
    api_client.force_authenticate(user=create_review.user)
    response = api_client.delete(reverse('review_detail', args=[create_review.id]))
    assert response.status_code == 204
    assert Review.objects.filter(id=create_review.id).exists() is False
