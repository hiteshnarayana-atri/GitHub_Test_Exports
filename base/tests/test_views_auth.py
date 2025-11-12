import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

def test_create_room_requires_login(client):
    r = client.get(reverse("create-room"))
    assert r.status_code in (302, 301)
    assert "login" in r.url

def test_host_can_update_room(client_logged_in, room):
    r = client_logged_in.get(reverse("update-room", args=[room.id]))
    assert r.status_code == 302

def test_non_host_cannot_update_room(client, other_user, room):
    client.login(username="bob", password="pass12345")
    r = client.get(reverse("update-room", args=[room.id]))
    assert r.status_code in (302, 403)