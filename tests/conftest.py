import os
import sqlite3
import tempfile
import pytest
from werkzeug.security import generate_password_hash
from app import app as flask_app
from database.db import init_db, DATABASE, get_db


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


@pytest.fixture
def registered_user(app):
    """Insert a user but do NOT log in."""
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ('Jane Doe', 'jane@example.com', generate_password_hash('password123'))
        )
        db.commit()
        db.close()


@pytest.fixture
def logged_in_client(client, registered_user):
    """Client with an active session."""
    client.post('/login', data={
        'email': 'jane@example.com',
        'password': 'password123'
    })
    return client
