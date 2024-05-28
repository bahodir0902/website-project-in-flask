import pytest
from app import app as flask_app


@pytest.fixture
def app():
    return flask_app


def test_login(client):
    response = client.get('/login')
    print(response.data)