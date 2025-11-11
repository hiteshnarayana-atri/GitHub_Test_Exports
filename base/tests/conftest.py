import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
import xml.dom.minidom


User = get_user_model()

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    xml_file = session.config.option.xmlpath
    if xml_file:
        with open(xml_file, 'r') as f:
            dom = xml.dom.minidom.parse(f)
        with open(xml_file, 'w') as f:
            f.write(dom.toprettyxml(indent="  "))

@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", 
                                    email="testuser@example.com",
                                    password="password")

@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="otheruser", 
                                    email="otheruser@example.com",
                                    password="pass12344")

@pytest.fixture
def topic(db):
    return baker.make("base.Topic", name="Django")

@pytest.fixture
def room(db, user, topic):
    return baker.make(
        "base.Room",
        host=user,
        topic=topic,
        name="Test Room",
        description="A room for testing",
    )

@pytest.fixture
def message(db, user, room):
    return baker.make(
        "base.Message",
        user=user,
        room=room,
        body="This is a test message.",
    )

@pytest.fixture
def client_logged_in(client, user):
    client.login(username="testuser", password="password")
    return client
