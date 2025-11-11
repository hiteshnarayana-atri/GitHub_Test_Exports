import pytest
from base.models import Message

pytestmark = pytest.mark.django_db

def test_topic_str(topic):
    assert str(topic) == "Django"

def test_room_str(room):
    assert "Test Room" in str(room)

def test_message_links_user_and_room(db, user, room):
    m = Message.objects.create(user=user, room=room, body="hello")
    assert m.user == user and m.room == room and "hello" in str(m)
