import pytest
from werkzeug.security import generate_password_hash
from database.db import get_db


@pytest.fixture
def test_expenses_fixture(app, registered_user):
    """Insert three test expenses at different dates"""
    with app.app_context():
        db = get_db()
        user = db.execute("SELECT id FROM users WHERE email = ?", ('jane@example.com',)).fetchone()
        db.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (user['id'], 100.00, 'Food', '2026-04-01', 'Early expense')
        )
        db.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (user['id'], 200.00, 'Transport', '2026-04-15', 'Mid-range expense')
        )
        db.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (user['id'], 300.00, 'Entertainment', '2026-04-20', 'Late expense')
        )
        db.commit()
        db.close()
    return True


class TestDateFilter:
    """Tests for date filtering on the profile page"""

    def test_no_filter_shows_all_expenses(self, logged_in_client, test_expenses_fixture):
        """Without date filter, all expenses should be shown"""
        response = logged_in_client.get('/profile')
        assert response.status_code == 200
        assert b'100.00' in response.data
        assert b'200.00' in response.data
        assert b'300.00' in response.data
        assert b'Early expense' in response.data
        assert b'Mid-range expense' in response.data
        assert b'Late expense' in response.data

    def test_filter_both_dates(self, logged_in_client, test_expenses_fixture):
        """Filter with start and end date should show only matching expenses"""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-10',
            'end_date': '2026-04-20'
        })
        assert response.status_code == 200
        assert b'100.00' not in response.data  # Before range
        assert b'200.00' in response.data      # In range
        assert b'300.00' in response.data      # In range
        assert b'Early expense' not in response.data
        assert b'Mid-range expense' in response.data
        assert b'Late expense' in response.data

    def test_filter_start_date_only(self, logged_in_client, test_expenses_fixture):
        """Filter with only start_date should show expenses from that date onward"""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-15'
        })
        assert response.status_code == 200
        assert b'100.00' not in response.data  # Before start
        assert b'200.00' in response.data      # On start
        assert b'300.00' in response.data      # After start
        assert b'Early expense' not in response.data
        assert b'Mid-range expense' in response.data
        assert b'Late expense' in response.data

    def test_filter_end_date_only(self, logged_in_client, test_expenses_fixture):
        """Filter with only end_date should show expenses up to that date"""
        response = logged_in_client.get('/profile', query_string={
            'end_date': '2026-04-10'
        })
        assert response.status_code == 200
        assert b'100.00' in response.data      # Before end
        assert b'200.00' not in response.data  # After end
        assert b'300.00' not in response.data  # After end
        assert b'Early expense' in response.data
        assert b'Mid-range expense' not in response.data
        assert b'Late expense' not in response.data

    def test_filter_invalid_range_start_after_end(self, logged_in_client, test_expenses_fixture):
        """Filter with start_date > end_date should show error and redirect"""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-30',
            'end_date': '2026-04-01'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Start date must be before end date.' in response.data
        # Should still show all expenses after redirect
        assert b'100.00' in response.data
        assert b'200.00' in response.data
        assert b'300.00' in response.data

    def test_filter_no_results(self, logged_in_client, test_expenses_fixture):
        """Filter with no matching expenses should show contextual empty message"""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2020-01-01',
            'end_date': '2020-01-02'
        })
        assert response.status_code == 200
        assert b'No expenses found for the selected date range.' in response.data
        # No expense amounts should be visible
        assert b'100.00' not in response.data
        assert b'200.00' not in response.data
        assert b'300.00' not in response.data

    def test_filter_stats_update(self, logged_in_client, app, test_expenses_fixture):
        """Stats should update to reflect only filtered expenses"""
        # Test filter showing only middle and late expenses (200 + 300 = 500)
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-10',
            'end_date': '2026-04-20'
        })
        assert response.status_code == 200
        assert b'500.00' in response.data  # Total of 200 + 300
        assert b'2' in response.data       # Count = 2 expenses
        assert b'250.00' in response.data  # Average = 500 / 2

    def test_filter_active_indicator_shown(self, logged_in_client, test_expenses_fixture):
        """When a filter is applied, active indicator should be shown"""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-10'
        })
        assert response.status_code == 200
        assert b'Showing:' in response.data
        assert b'2026-04-10' in response.data

    def test_filter_cleared(self, logged_in_client, test_expenses_fixture):
        """After clearing filter, all expenses should be visible again"""
        # First apply a filter
        logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-15'
        })
        # Then clear it by visiting without params
        response = logged_in_client.get('/profile')
        assert response.status_code == 200
        assert b'100.00' in response.data
        assert b'200.00' in response.data
        assert b'300.00' in response.data
        # No filter indicator should be shown
        assert b'Showing:' not in response.data

    def test_filter_params_preserved_in_form(self, logged_in_client, test_expenses_fixture):
        """Applied filter values should be preserved in the form inputs"""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-10',
            'end_date': '2026-04-20'
        })
        assert response.status_code == 200
        assert b'value="2026-04-10"' in response.data
        assert b'value="2026-04-20"' in response.data

    def test_filter_only_user_expenses(self, app, client, registered_user):
        """Filter should only apply to current user's expenses, not other users"""
        with app.app_context():
            db = get_db()
            user = db.execute("SELECT id FROM users WHERE email = ?", ('jane@example.com',)).fetchone()

            # Insert another user
            db.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                ('John Doe', 'john@example.com', generate_password_hash('password123'))
            )
            db.commit()
            other_user = db.execute("SELECT id FROM users WHERE email = ?", ('john@example.com',)).fetchone()

            # Insert expenses for both users
            db.execute(
                "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
                (user['id'], 100.00, 'Food', '2026-04-15')
            )
            db.execute(
                "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
                (other_user['id'], 999.00, 'Food', '2026-04-15')
            )
            db.commit()
            db.close()

        # Log in as jane and apply filter
        client.post('/login', data={'email': 'jane@example.com', 'password': 'password123'})
        response = client.get('/profile', query_string={
            'start_date': '2026-04-15',
            'end_date': '2026-04-15'
        })
        assert response.status_code == 200
        assert b'100.00' in response.data
        assert b'999.00' not in response.data  # Other user's expense should not appear

    def test_profile_post_clears_filter(self, logged_in_client, app, test_expenses_fixture):
        """After profile update (POST), filter should be cleared on redirect"""
        # Apply a filter
        logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-15'
        })
        # Update profile (POST)
        response = logged_in_client.post('/profile', data={
            'name': 'Jane Updated'
        }, follow_redirects=True)
        assert response.status_code == 200
        # After redirect, all expenses should be visible (no filter)
        assert b'100.00' in response.data
        assert b'200.00' in response.data
        assert b'300.00' in response.data
        assert b'Showing:' not in response.data
