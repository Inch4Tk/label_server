import os
import tempfile
import pytest

from flask_label import create_app
from flask_label.db import get_db, init_db
import flask_label.config

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    DATABASE_FILEDESCRIPTOR, DATABASE = tempfile.mkstemp()
    test_config = flask_label.config.Testing()
    test_config.DATABASE = DATABASE
    app = create_app(test_config)

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(DATABASE_FILEDESCRIPTOR)
    os.unlink(DATABASE)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login",
            data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)