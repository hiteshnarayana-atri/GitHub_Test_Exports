import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='other', email='o@x.com', password='pass')

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
def test_list_requires_auth(api_client):
    url = reverse('notification-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_list_notifications(authenticated_client, user):
    Notification.objects.create(user=user, notification_type=Notification.ROOM_CREATED, message='n1')
    Notification.objects.create(user=user, notification_type=Notification.MESSAGE_RECEIVED, message='n2')
    url = reverse('notification-list')
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

@pytest.mark.django_db
def test_unread_count_endpoint(authenticated_client, user):
    Notification.objects.create(user=user, notification_type=Notification.ROOM_CREATED, message='u1')
    Notification.objects.create(user=user, notification_type=Notification.ROOM_CREATED, message='u2', is_read=True)
    url = reverse('notification-unread-count')
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['unread_count'] == 1




