import pytest
from werkzeug.security import check_password_hash
from database.db import get_db


def test_register_get(client):
    """Test GET /register returns form with 200 status."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Create your account' in response.data
    assert b'Full name' in response.data
    assert b'Email address' in response.data
    assert b'Password' in response.data


def test_register_success(client, app):
    """Test valid registration creates user and redirects to login."""
    response = client.post('/register', data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'password123'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert response.location.endswith('/login')

    # Verify user was created in database
    with app.app_context():
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?", ('john@example.com',)
        ).fetchone()
        db.close()

        assert user is not None
        assert user['name'] == 'John Doe'
        assert user['email'] == 'john@example.com'
        assert check_password_hash(user['password'], 'password123')


def test_register_missing_fields(client):
    """Test empty fields show error message."""
    response = client.post('/register', data={
        'name': '',
        'email': '',
        'password': ''
    })

    assert response.status_code == 200
    assert b'All fields are required.' in response.data


def test_register_short_password(client):
    """Test password less than 8 characters shows error."""
    response = client.post('/register', data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'short'
    })

    assert response.status_code == 200
    assert b'Password must be at least 8 characters long.' in response.data


def test_register_duplicate_email(client, app):
    """Test duplicate email shows error message."""
    # Register first user
    client.post('/register', data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'password123'
    })

    # Try to register with same email
    response = client.post('/register', data={
        'name': 'Jane Doe',
        'email': 'john@example.com',
        'password': 'password456'
    })

    assert response.status_code == 200
    assert b'Email already registered.' in response.data


def test_password_is_hashed(client, app):
    """Test password is stored hashed, not plaintext."""
    plaintext = 'mypassword123'
    client.post('/register', data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': plaintext
    })

    with app.app_context():
        db = get_db()
        user = db.execute(
            "SELECT password FROM users WHERE email = ?", ('john@example.com',)
        ).fetchone()
        db.close()

        assert user is not None
        # Password should be hashed, not plaintext
        assert user['password'] != plaintext
        # But it should still validate correctly
        assert check_password_hash(user['password'], plaintext)


def test_email_stored_lowercase(client, app):
    """Test email is normalized to lowercase."""
    response = client.post('/register', data={
        'name': 'John Doe',
        'email': 'John@Example.COM',
        'password': 'password123'
    }, follow_redirects=False)

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        user = db.execute(
            "SELECT email FROM users WHERE email = ?", ('john@example.com',)
        ).fetchone()
        db.close()

        assert user is not None
        assert user['email'] == 'john@example.com'


def test_register_whitespace_fields(client):
    """Test whitespace-only fields treated as empty."""
    response = client.post('/register', data={
        'name': '   ',
        'email': '   ',
        'password': '   '
    })

    assert response.status_code == 200
    assert b'All fields are required.' in response.data


def test_register_success_flash_message(client):
    """Test success flash message appears after registration."""
    response = client.post('/register', data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Account created. Please log in.' in response.data


def test_register_field_repopulation_on_error(client):
    """Test form fields are repopulated on validation error."""
    response = client.post('/register', data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'short'
    })

    assert response.status_code == 200
    # Check that name and email are preserved in form
    assert b'value="John Doe"' in response.data
    assert b'value="john@example.com"' in response.data
