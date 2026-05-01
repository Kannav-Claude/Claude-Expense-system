import os
import sqlite3
import tempfile
import pytest
from app import app as flask_app
from database.db import init_db, DATABASE


@pytest.fixture
def app():
    # Create a temporary database file for testing
    db_fd, db_path = tempfile.mkstemp()

    # Configure the app for testing
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key'

    # Override DATABASE path to use temp file
    import database.db as db_module
    original_db = db_module.DATABASE
    db_module.DATABASE = db_path

    # Initialize the database
    with flask_app.app_context():
        init_db()

    yield flask_app

    # Cleanup
    db_module.DATABASE = original_db
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
