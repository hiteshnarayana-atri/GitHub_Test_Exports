import pytest
from django.contrib.auth import get_user_model
from notifications.models import Notification

# optional import depending on availability of base app:
try:
    from base.models import Room, Topic
    HAS_BASE = True
except ImportError:
    HAS_BASE = False

User = get_user_model()

@pytest.mark.skipif(not HAS_BASE, reason="base app not available")
@pytest.mark.django_db

def test_room_create_triggers_notifications():
    """The testcase fails
        if the base app is not present, as signals depend on it.

        *Also I have changed it notify all including the host*
    """
    host = User.objects.create_user(username='host', email='host@example.com', password='1')
    user1 = User.objects.create_user(username='u1', email='u1@example.com', password='1')
    user2 = User.objects.create_user(username='u2', email='u2@example.com', password='1')
    topic = Topic.objects.create(name='Test')
    Room.objects.create(host=host, topic=topic, name='r1', description='d')
    notifications = Notification.objects.filter(notification_type=Notification.ROOM_CREATED)
    assert notifications.count() >= 1
    assert not notifications.filter(user=host).exists()
