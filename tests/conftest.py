import os
import tempfile
import pytest

from flask_label import create_app
from flask_label.database_cli import db_init_users, db_update_task
import flask_label.config

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    DATABASE_FILEDESCRIPTOR, DATABASE = tempfile.mkstemp()
    test_config = flask_label.config.Testing()
    test_config.DATABASE = DATABASE
    test_config.SQLALCHEMY_DATABASE_URI = "sqlite:////{}".format(DATABASE)
    app = create_app(test_config)

    with app.app_context():
        from flask_migrate import upgrade as _upgrade
        _upgrade()
        db_init_users()
        db_update_task()

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