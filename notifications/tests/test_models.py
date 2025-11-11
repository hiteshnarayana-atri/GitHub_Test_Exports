import pytest
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()

@pytest.mark.django_db
def test_notification_creation_and_read():
    user = User.objects.create_user(username='demo', email='demo@example.com', password='123')
    notification = Notification.objects.create(
        user=user,
        notification_type=Notification.ROOM_CREATED,
        message='Test message',
        link='/room/1/'
    )
    assert notification.user == user
    assert notification.is_read is False
    notification.mark_as_read()
    assert notification.is_read is True
