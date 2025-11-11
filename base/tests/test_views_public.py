import pytest 
from django.urls import reverse,resolve
from base import views

def test_home_url_resolves():
    path = reverse("home")
    assert resolve(path).func == views.home

def test_home_renders(client,db):
    r = client.get(reverse("home"))
    assert r.status_code == 200
    assert "topics" in r.context or "rooms" in r.context


def test_room_detail_renders(client, room,db):
    r = client.get(reverse("room", args=[room.id]))
    assert r.status_code == 200
    assert r.context["room"].id == room.id
