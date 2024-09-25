import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from listings.models import Listing

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_users():
    tenant = User.objects.create_user(email='tenant@example.com', password='tenantpass', role='tenant')
    landlord = User.objects.create_user(email='landlord@example.com', password='landlordpass', role='landlord')
    return tenant, landlord

@pytest.mark.django_db
def test_create_listing(api_client, create_users):
    _, landlord = create_users
    api_client.force_authenticate(user=landlord)
    response = api_client.post(
        reverse('listings'),
        {
            'title': 'Test Listing',
            'description': 'Beautiful place in the city',
            'location': 'Test City',
            'price': 100,
            'rooms': 2,
            'type': 'apartment'
        }
    )
    assert response.status_code == 201
    assert Listing.objects.count() == 1

@pytest.mark.django_db
def test_view_listings(api_client, create_users):
    _, landlord = create_users
    listing = Listing.objects.create(owner=landlord, title="Test Listing", location="Test City")
    response = api_client.get(reverse('listings'))
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
def test_update_listing(api_client, create_users):
    _, landlord = create_users
    listing = Listing.objects.create(owner=landlord, title="Old Title", location="Test City")
    api_client.force_authenticate(user=landlord)
    response = api_client.patch(
        reverse('listing_detail', args=[listing.id]),
        {'title': 'Updated Title'}
    )
    assert response.status_code == 200
    listing.refresh_from_db()
    assert listing.title == 'Updated Title'

@pytest.mark.django_db
def test_delete_listing(api_client, create_users):
    _, landlord = create_users
    listing = Listing.objects.create(owner=landlord, title="Test Listing", location="Test City")
    api_client.force_authenticate(user=landlord)
    response = api_client.delete(reverse('listing_detail', args=[listing.id]))
    assert response.status_code == 204
    assert Listing.objects.filter(id=listing.id).exists() is False

@pytest.mark.django_db
def test_tenant_cannot_modify_listing(api_client, create_users):
    tenant, landlord = create_users
    listing = Listing.objects.create(owner=landlord, title="Test Listing", location="Test City")
    api_client.force_authenticate(user=tenant)
    response = api_client.patch(
        reverse('listing_detail', args=[listing.id]),
        {'title': 'Attempted Update'}
    )
    assert response.status_code == 403  # Проверка, что арендатор не может редактировать объявления
