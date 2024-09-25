import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from listings.models import Listing, Booking

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
        status='pending'
    )

@pytest.mark.django_db
def test_create_booking(api_client, create_users, create_listing):
    tenant, _ = create_users
    api_client.force_authenticate(user=tenant)
    response = api_client.post(
        reverse('booking_list_create'),
        {'listing': create_listing.id, 'start_date': '2024-09-20', 'end_date': '2024-09-25'}
    )
    assert response.status_code == 201
    assert Booking.objects.count() == 1

@pytest.mark.django_db
def test_cancel_booking(api_client, create_booking):
    api_client.force_authenticate(user=create_booking.user)
    response = api_client.patch(
        reverse('booking_detail', args=[create_booking.id]),
        {'status': 'cancelled'}
    )
    assert response.status_code == 200
    create_booking.refresh_from_db()
    assert create_booking.status == 'cancelled'

@pytest.mark.django_db
def test_confirm_booking(api_client, create_users, create_booking):
    _, landlord = create_users
    api_client.force_authenticate(user=landlord)
    response = api_client.patch(
        reverse('booking_detail', args=[create_booking.id]),
        {'status': 'confirmed'}
    )
    assert response.status_code == 200
    create_booking.refresh_from_db()
    assert create_booking.status == 'confirmed'

@pytest.mark.django_db
def test_delete_booking(api_client, create_users, create_booking):
    _, landlord = create_users
    api_client.force_authenticate(user=landlord)
    create_booking.status = 'confirmed'
    create_booking.save()
    response = api_client.delete(reverse('booking_detail', args=[create_booking.id]))
    assert response.status_code == 204
    assert Booking.objects.filter(id=create_booking.id).exists() is False
