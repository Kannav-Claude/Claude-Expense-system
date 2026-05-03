import pytest
from werkzeug.security import generate_password_hash
from database.db import get_db


@pytest.fixture
def auth_user(app):
    """Create a test user in the database for login tests."""
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ('John Doe', 'john@example.com', generate_password_hash('password123'))
        )
        db.commit()
        db.close()


def test_login_get(client):
    """Test GET /login returns form with 200 status."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Welcome back' in response.data
    assert b'Sign in to your Spendly account' in response.data
    assert b'Email address' in response.data
    assert b'Password' in response.data


def test_login_valid_credentials(client, auth_user):
    """Test valid login creates session and redirects to profile."""
    response = client.post('/login', data={
        'email': 'john@example.com',
        'password': 'password123'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert response.location.endswith('/profile')

    # Verify session was created
    with client.session_transaction() as sess:
        assert sess['user_id'] == 1
        assert sess['user_name'] == 'John Doe'


def test_login_invalid_email(client):
    """Test login with non-existent email shows error."""
    response = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'password123'
    })

    assert response.status_code == 200
    assert b'Invalid email or password.' in response.data


def test_login_wrong_password(client, auth_user):
    """Test login with correct email but wrong password shows error."""
    response = client.post('/login', data={
        'email': 'john@example.com',
        'password': 'wrongpassword'
    })

    assert response.status_code == 200
    assert b'Invalid email or password.' in response.data


def test_login_missing_fields(client):
    """Test login with empty fields shows error."""
    response = client.post('/login', data={
        'email': '',
        'password': ''
    })

    assert response.status_code == 200
    assert b'Invalid email or password.' in response.data


def test_login_case_insensitive_email(client, auth_user):
    """Test login with uppercase email matches lowercase in database."""
    response = client.post('/login', data={
        'email': 'JOHN@EXAMPLE.COM',
        'password': 'password123'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert response.location.endswith('/profile')

    # Verify session was created
    with client.session_transaction() as sess:
        assert sess['user_id'] == 1


def test_logout(client, auth_user):
    """Test logout clears session and redirects to landing."""
    # First login
    client.post('/login', data={
        'email': 'john@example.com',
        'password': 'password123'
    })

    # Verify session exists
    with client.session_transaction() as sess:
        assert 'user_id' in sess

    # Logout
    response = client.get('/logout', follow_redirects=False)

    assert response.status_code == 302
    assert response.location.endswith('/')

    # Verify session is cleared
    with client.session_transaction() as sess:
        assert 'user_id' not in sess


def test_protected_route_requires_login(client):
    """Test accessing /expenses without login redirects to /login."""
    response = client.get('/expenses', follow_redirects=False)

    assert response.status_code == 302
    assert response.location.endswith('/login')
