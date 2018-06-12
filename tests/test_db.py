import sqlite3

import pytest


def test_db_init_user_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_db_init_user():
        Recorder.called = True

    monkeypatch.setattr("flask_label.database_cli.db_init_users", fake_db_init_user)
    result = runner.invoke(args=["db-init-user"])
    assert "Initialized" in result.output
    assert Recorder.called


def test_db_update_task_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_db_update_task():
        Recorder.called = True

    monkeypatch.setattr("flask_label.database_cli.db_update_task", fake_db_update_task)
    result = runner.invoke(args=["db-update-task"])
    assert "Updated" in result.output
    assert Recorder.called


def test_db_drop_all_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_db_drop_all():
        Recorder.called = True

    monkeypatch.setattr("flask_label.database_cli.db_drop_all", fake_db_drop_all)
    result = runner.invoke(args=["db-drop-all"])
    assert "Cleared" in result.output
    assert Recorder.called