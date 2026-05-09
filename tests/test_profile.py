import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db


# ------------------------------------------------------------------ #
# Auth guard                                                           #
# ------------------------------------------------------------------ #

def test_profile_requires_login_get(client):
    """GET /profile without session redirects to /login."""
    response = client.get('/profile', follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith('/login')


def test_profile_requires_login_post(client):
    """POST /profile without session redirects to /login."""
    response = client.post('/profile', data={'name': 'X'}, follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith('/login')


# ------------------------------------------------------------------ #
# GET /profile                                                         #
# ------------------------------------------------------------------ #

def test_profile_get_returns_200(logged_in_client):
    response = logged_in_client.get('/profile')
    assert response.status_code == 200


def test_profile_get_shows_user_name(logged_in_client):
    response = logged_in_client.get('/profile')
    assert b'Jane Doe' in response.data


def test_profile_get_shows_user_email(logged_in_client):
    response = logged_in_client.get('/profile')
    assert b'jane@example.com' in response.data


def test_profile_get_email_field_is_disabled(logged_in_client):
    """Email input must carry the disabled attribute."""
    response = logged_in_client.get('/profile')
    assert b'disabled' in response.data


def test_profile_get_shows_stats_with_no_expenses(logged_in_client):
    """Stats render with zero values when user has no expenses."""
    response = logged_in_client.get('/profile')
    assert b'0' in response.data
    assert b'0.00' in response.data


def test_profile_get_shows_stats_with_expenses(logged_in_client, app):
    """Stats show correct totals when expenses exist."""
    with app.app_context():
        db = get_db()
        user = db.execute(
            "SELECT id FROM users WHERE email = ?", ('jane@example.com',)
        ).fetchone()
        db.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
            (user['id'], 500.00, 'Food', '2026-04-01')
        )
        db.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
            (user['id'], 300.00, 'Transport', '2026-04-02')
        )
        db.commit()
        db.close()

    response = logged_in_client.get('/profile')
    assert b'800.00' in response.data
    assert b'Food' in response.data
    assert b'Transport' in response.data


# ------------------------------------------------------------------ #
# POST /profile — name update only                                     #
# ------------------------------------------------------------------ #

def test_profile_post_name_update(logged_in_client, app):
    """Valid name update succeeds and redirects."""
    response = logged_in_client.post('/profile', data={
        'name': 'Jane Smith',
        'new_password': '',
        'confirm_password': ''
    }, follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith('/profile')

    with app.app_context():
        db = get_db()
        user = db.execute(
            "SELECT name FROM users WHERE email = ?", ('jane@example.com',)
        ).fetchone()
        db.close()
        assert user['name'] == 'Jane Smith'


def test_profile_post_name_update_flash_success(logged_in_client):
    response = logged_in_client.post('/profile', data={
        'name': 'Jane Smith',
        'new_password': '',
        'confirm_password': ''
    }, follow_redirects=True)
    assert b'Profile updated.' in response.data


def test_profile_post_empty_name_rejected(logged_in_client):
    response = logged_in_client.post('/profile', data={
        'name': '',
        'new_password': '',
        'confirm_password': ''
    })
    assert response.status_code == 200
    assert b'Name cannot be empty.' in response.data


def test_profile_post_whitespace_name_rejected(logged_in_client):
    response = logged_in_client.post('/profile', data={
        'name': '   ',
        'new_password': '',
        'confirm_password': ''
    })
    assert b'Name cannot be empty.' in response.data


# ------------------------------------------------------------------ #
# POST /profile — password change                                      #
# ------------------------------------------------------------------ #

def test_profile_post_password_change_valid(logged_in_client, app):
    response = logged_in_client.post('/profile', data={
        'name': 'Jane Doe',
        'new_password': 'newpassword99',
        'confirm_password': 'newpassword99'
    }, follow_redirects=False)
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        user = db.execute(
            "SELECT password FROM users WHERE email = ?", ('jane@example.com',)
        ).fetchone()
        db.close()
        assert check_password_hash(user['password'], 'newpassword99')


def test_profile_post_password_too_short(logged_in_client):
    response = logged_in_client.post('/profile', data={
        'name': 'Jane Doe',
        'new_password': 'short',
        'confirm_password': 'short'
    })
    assert response.status_code == 200
    assert b'at least 8 characters' in response.data


def test_profile_post_password_mismatch(logged_in_client):
    response = logged_in_client.post('/profile', data={
        'name': 'Jane Doe',
        'new_password': 'newpassword99',
        'confirm_password': 'different99'
    })
    assert response.status_code == 200
    assert b'Passwords do not match.' in response.data


def test_profile_post_password_not_changed_when_blank(logged_in_client, app):
    """Submitting empty password fields must NOT alter the stored hash."""
    with app.app_context():
        db = get_db()
        original_hash = db.execute(
            "SELECT password FROM users WHERE email = ?", ('jane@example.com',)
        ).fetchone()['password']
        db.close()

    logged_in_client.post('/profile', data={
        'name': 'Jane Doe',
        'new_password': '',
        'confirm_password': ''
    })

    with app.app_context():
        db = get_db()
        new_hash = db.execute(
            "SELECT password FROM users WHERE email = ?", ('jane@example.com',)
        ).fetchone()['password']
        db.close()

    assert original_hash == new_hash


# ------------------------------------------------------------------ #
# Session sync                                                         #
# ------------------------------------------------------------------ #

def test_profile_post_updates_session_user_name(logged_in_client):
    """After name update, session['user_name'] should reflect the new name."""
    logged_in_client.post('/profile', data={
        'name': 'Jane Updated',
        'new_password': '',
        'confirm_password': ''
    })
    with logged_in_client.session_transaction() as sess:
        assert sess['user_name'] == 'Jane Updated'


# ------------------------------------------------------------------ #
# Email immutability                                                   #
# ------------------------------------------------------------------ #

def test_profile_post_cannot_change_email(logged_in_client, app):
    """Even if the form somehow sent an email field, the DB email is unchanged."""
    logged_in_client.post('/profile', data={
        'name': 'Jane Doe',
        'email': 'hacker@evil.com',
        'new_password': '',
        'confirm_password': ''
    })
    with app.app_context():
        db = get_db()
        user = db.execute(
            "SELECT email FROM users WHERE id = ?",
            (1,)
        ).fetchone()
        db.close()
        assert user['email'] == 'jane@example.com'
