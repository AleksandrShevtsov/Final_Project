import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_user_registration(api_client):
    response = api_client.post(
        reverse('register'),
        {
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'role': 'tenant',
            'first_name': 'John',
            'last_name': 'Doe'
        }
    )
    assert response.status_code == 201
    assert User.objects.filter(email='testuser@example.com').exists()

@pytest.mark.django_db
def test_user_login(api_client):
    user = User.objects.create_user(email='testlogin@example.com', password='testpass', role='tenant')
    response = api_client.post(
        reverse('login'),
        {'email': 'testlogin@example.com', 'password': 'testpass'}
    )
    assert response.status_code == 200
    assert 'access_token' in response.cookies  # Проверяем, что токен добавлен в куки

@pytest.mark.django_db
def test_user_roles(api_client):
    tenant = User.objects.create_user(email='tenant@example.com', password='tenantpass', role='tenant')
    landlord = User.objects.create_user(email='landlord@example.com', password='landlordpass', role='landlord')
    assert tenant.role == 'tenant'
    assert landlord.role == 'landlord'
