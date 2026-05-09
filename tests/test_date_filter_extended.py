"""
Extended pytest test suite for Step 04: Date Filter on the Profile Page.

These tests complement the 12 tests already in test_date_filter.py.
They cover boundary conditions, indicator text variants, stats edge cases,
currency rendering, security, ordering guarantees, and robustness against
malformed or unexpected input.

All tests use the fixtures defined in conftest.py (app, client,
registered_user, logged_in_client) and a local fixture that inserts a
richer set of expenses to support the additional scenarios.
"""

import pytest
from database.db import get_db
from werkzeug.security import generate_password_hash


# ------------------------------------------------------------------ #
# Fixtures                                                            #
# ------------------------------------------------------------------ #

@pytest.fixture
def multi_expense_fixture(app, registered_user):
    """
    Insert five expenses spread across several dates and categories.
    Amounts are chosen so that sub-range totals produce unambiguous values.

    Expenses inserted:
        2026-03-01  Food          500.00  'March start'
        2026-04-01  Transport     200.00  'April first'
        2026-04-15  Bills         300.00  'April mid'
        2026-04-15  Health        100.00  'April mid second'   <- same date, different row
        2026-05-01  Shopping      750.00  'May start'
    """
    with app.app_context():
        db = get_db()
        user = db.execute(
            "SELECT id FROM users WHERE email = ?", ('jane@example.com',)
        ).fetchone()
        uid = user['id']
        rows = [
            (uid, 500.00, 'Food',      '2026-03-01', 'March start'),
            (uid, 200.00, 'Transport', '2026-04-01', 'April first'),
            (uid, 300.00, 'Bills',     '2026-04-15', 'April mid'),
            (uid, 100.00, 'Health',    '2026-04-15', 'April mid second'),
            (uid, 750.00, 'Shopping',  '2026-05-01', 'May start'),
        ]
        db.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description)"
            " VALUES (?, ?, ?, ?, ?)",
            rows
        )
        db.commit()
        db.close()
    return True


@pytest.fixture
def second_user_fixture(app, registered_user):
    """
    Create a second user (bob@example.com) with one expense on 2026-04-15.
    Used to verify that cross-user data never leaks through the filter.
    """
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ('Bob Smith', 'bob@example.com', generate_password_hash('password123'))
        )
        db.commit()
        bob = db.execute(
            "SELECT id FROM users WHERE email = ?", ('bob@example.com',)
        ).fetchone()
        db.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description)"
            " VALUES (?, ?, ?, ?, ?)",
            (bob['id'], 9999.00, 'Food', '2026-04-15', "Bob's secret expense")
        )
        db.commit()
        db.close()
    return True


# ------------------------------------------------------------------ #
# Boundary: same-day filter (start_date == end_date)                  #
# ------------------------------------------------------------------ #

class TestSameDayFilter:
    """
    When start_date and end_date are equal the route spec says the range is
    inclusive on both ends.  Expenses on that exact date must appear; those on
    any other date must not.
    """

    def test_same_day_filter_shows_matching_expense(
        self, logged_in_client, multi_expense_fixture
    ):
        """An expense whose date equals both start_date and end_date is shown."""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-01',
            'end_date': '2026-04-01',
        })
        assert response.status_code == 200
        assert b'April first' in response.data

    def test_same_day_filter_excludes_other_dates(
        self, logged_in_client, multi_expense_fixture
    ):
        """Expenses on dates outside the single-day window are excluded."""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-01',
            'end_date': '2026-04-01',
        })
        assert b'March start' not in response.data
        assert b'April mid' not in response.data
        assert b'May start' not in response.data

    def test_same_day_filter_stats_reflect_single_day(
        self, logged_in_client, multi_expense_fixture
    ):
        """Stats for a single-day filter with one matching expense: total=200, count=1, avg=200."""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-01',
            'end_date': '2026-04-01',
        })
        assert b'200.00' in response.data   # total and avg are identical for count=1
        assert b'1' in response.data

    def test_same_day_filter_with_multiple_expenses_on_that_date(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        When two expenses share the same date and a single-day filter targets
        that date, both expenses must appear and stats must aggregate both.
        April 15 has 300 + 100 = 400, count 2, avg 200.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-15',
            'end_date': '2026-04-15',
        })
        assert response.status_code == 200
        assert b'April mid' in response.data
        assert b'April mid second' in response.data
        assert b'400.00' in response.data   # total
        assert b'200.00' in response.data   # avg


# ------------------------------------------------------------------ #
# Filter active indicator text variants                               #
# ------------------------------------------------------------------ #

class TestFilterActiveIndicatorText:
    """
    The template renders:
        Showing: {{ start_date or 'Beginning' }} — {{ end_date or 'Today' }}
    Each combination of omitted/present param should produce the correct text.
    """

    def test_indicator_shows_beginning_when_only_end_date_set(
        self, logged_in_client, multi_expense_fixture
    ):
        """Only end_date supplied: indicator must contain 'Beginning'."""
        response = logged_in_client.get('/profile', query_string={
            'end_date': '2026-04-15',
        })
        assert response.status_code == 200
        assert b'Beginning' in response.data

    def test_indicator_shows_today_when_only_start_date_set(
        self, logged_in_client, multi_expense_fixture
    ):
        """Only start_date supplied: indicator must contain 'Today'."""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-01',
        })
        assert response.status_code == 200
        assert b'Today' in response.data

    def test_indicator_shows_both_dates_when_both_set(
        self, logged_in_client, multi_expense_fixture
    ):
        """Both params supplied: indicator must contain both date strings."""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-01',
            'end_date': '2026-04-15',
        })
        assert b'2026-04-01' in response.data
        assert b'2026-04-15' in response.data

    def test_indicator_absent_when_no_filter_applied(
        self, logged_in_client, multi_expense_fixture
    ):
        """No filter params: the active indicator block must not appear at all."""
        response = logged_in_client.get('/profile')
        assert b'Showing:' not in response.data
        assert b'Beginning' not in response.data
        assert b'Today' not in response.data


# ------------------------------------------------------------------ #
# Stats edge cases                                                    #
# ------------------------------------------------------------------ #

class TestFilteredStats:
    """
    Verify that the three stats values (total, count, average) remain
    accurate under various filter conditions.
    """

    def test_stats_are_zero_when_filter_matches_no_expenses(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        When the filter produces an empty result set the stats should show
        0 for count, 0.00 for total and average — not a server error.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2000-01-01',
            'end_date': '2000-01-31',
        })
        assert response.status_code == 200
        # Both total_spent and avg_expense rendered as 0.00 via COALESCE in SQL
        assert b'0.00' in response.data

    def test_stats_total_across_multiple_expenses_in_range(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        April 1 through April 15 inclusive: 200 + 300 + 100 = 600 total,
        3 expenses, avg = 200.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-01',
            'end_date': '2026-04-15',
        })
        assert response.status_code == 200
        assert b'600.00' in response.data   # total
        assert b'200.00' in response.data   # avg
        # Count = 3; the digit 3 will appear somewhere in the rendered stats
        assert b'3' in response.data

    def test_stats_cover_all_expenses_when_range_is_unbounded(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        No filter params: total must equal the sum of all five inserted rows
        500 + 200 + 300 + 100 + 750 = 1850.
        """
        response = logged_in_client.get('/profile')
        assert response.status_code == 200
        assert b'1850.00' in response.data

    def test_stats_with_start_only_sums_from_cutoff(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        start_date=2026-04-15: rows on/after Apr 15 are 300 + 100 + 750 = 1150,
        count=3, avg=383.33.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-15',
        })
        assert response.status_code == 200
        assert b'1150.00' in response.data


# ------------------------------------------------------------------ #
# INR currency rendering                                              #
# ------------------------------------------------------------------ #

class TestInrCurrencyRendering:
    """
    Per project constraints all monetary values must be displayed in INR.
    The template formats amounts with the ₹ symbol and two decimal places.
    """

    def test_inr_symbol_present_in_stats_total(
        self, logged_in_client, multi_expense_fixture
    ):
        """The total spent stat must be prefixed with the ₹ symbol."""
        response = logged_in_client.get('/profile')
        # ₹ in UTF-8 is the byte sequence b'\xe2\x82\xb9'
        assert '₹'.encode('utf-8') in response.data

    def test_inr_symbol_present_in_expense_list_amounts(
        self, logged_in_client, multi_expense_fixture
    ):
        """Each row in the expense table must display the ₹ symbol before its amount."""
        response = logged_in_client.get('/profile')
        # The template renders ₹{{ "%.2f"|format(expense['amount']) }} per row
        assert b'\xe2\x82\xb9500.00' in response.data   # 500.00 with ₹

    def test_filtered_expense_amounts_formatted_to_two_decimal_places(
        self, logged_in_client, multi_expense_fixture
    ):
        """Amounts in a filtered view must be shown with exactly two decimal places."""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-01',
            'end_date': '2026-04-01',
        })
        # 200 stored as DECIMAL(10,2) → rendered as 200.00
        assert b'200.00' in response.data


# ------------------------------------------------------------------ #
# Empty-state message distinction                                     #
# ------------------------------------------------------------------ #

class TestEmptyStateMessages:
    """
    Two distinct empty states exist:
        1. No expenses at all (filter_applied=False) → "No expenses yet."
        2. Filter active but no matches (filter_applied=True) → "No expenses found for the selected date range."
    Both must render correctly and must not be confused with each other.
    """

    def test_no_expenses_at_all_shows_generic_message(self, logged_in_client):
        """With zero expenses and no filter, the general empty prompt is shown."""
        response = logged_in_client.get('/profile')
        assert response.status_code == 200
        # The template renders "No expenses yet." for the unfiltered empty case
        assert b'No expenses yet.' in response.data
        # The filter-specific message must NOT appear
        assert b'No expenses found for the selected date range.' not in response.data

    def test_filter_empty_state_does_not_show_generic_message(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        When a filter is active and returns no results, only the filter-specific
        message appears; the generic "No expenses yet" prompt must not appear.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '1990-01-01',
            'end_date': '1990-01-01',
        })
        assert b'No expenses found for the selected date range.' in response.data
        assert b'No expenses yet.' not in response.data


# ------------------------------------------------------------------ #
# Expense list ordering                                               #
# ------------------------------------------------------------------ #

class TestExpenseListOrdering:
    """
    The route uses ORDER BY date ASC. Tests verify that filtered results
    are returned in ascending date order regardless of insertion order.
    """

    def test_unfiltered_results_ordered_ascending_by_date(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        Without a filter, expenses must appear in ascending date order.
        March start (2026-03-01) must appear before May start (2026-05-01)
        in the rendered HTML.
        """
        response = logged_in_client.get('/profile')
        html = response.data.decode('utf-8')
        march_pos = html.find('March start')
        may_pos = html.find('May start')
        assert march_pos != -1, "March start expense not found in response"
        assert may_pos != -1, "May start expense not found in response"
        assert march_pos < may_pos, (
            "Expenses are not in ascending date order: "
            f"March start at {march_pos}, May start at {may_pos}"
        )

    def test_filtered_results_ordered_ascending_by_date(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        With a filter that captures April expenses, April first (2026-04-01)
        must appear before April mid (2026-04-15) in the HTML.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-01',
            'end_date': '2026-04-30',
        })
        html = response.data.decode('utf-8')
        first_pos = html.find('April first')
        mid_pos = html.find('April mid')
        assert first_pos != -1, "April first expense not found in response"
        assert mid_pos != -1, "April mid expense not found in response"
        assert first_pos < mid_pos, (
            "Filtered expenses are not in ascending date order"
        )


# ------------------------------------------------------------------ #
# Security and access control                                         #
# ------------------------------------------------------------------ #

class TestFilterAccessControl:
    """
    Security tests ensuring the filter feature cannot be used to bypass
    authentication or leak data across user accounts.
    """

    def test_unauthenticated_request_with_filter_params_redirects_to_login(
        self, client
    ):
        """
        An anonymous GET to /profile with date filter params must redirect
        to /login, not expose any data.
        """
        response = client.get('/profile', query_string={
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert response.location.endswith('/login')

    def test_filter_does_not_expose_other_users_expenses(
        self, logged_in_client, second_user_fixture
    ):
        """
        Jane is logged in. Bob has an expense of 9999.00 on 2026-04-15.
        A filter targeting that exact date must not reveal Bob's expense.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-15',
            'end_date': '2026-04-15',
        })
        assert response.status_code == 200
        assert b'9999.00' not in response.data
        assert b"Bob's secret expense" not in response.data

    def test_filter_does_not_expose_other_users_stats(
        self, logged_in_client, second_user_fixture
    ):
        """
        The stats total must reflect only Jane's expenses even when a date
        range overlaps with Bob's expense dates.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
        })
        assert response.status_code == 200
        # Bob's 9999.00 must not appear in any stat
        assert b'9999' not in response.data


# ------------------------------------------------------------------ #
# Robustness: malformed and unexpected query parameters               #
# ------------------------------------------------------------------ #

class TestMalformedQueryParameters:
    """
    The application must not raise a 500 error for malformed or unexpected
    query parameters.  It should either treat them as absent (graceful
    degradation) or return a handled error response (400/redirect+flash).
    A 500 is always a failure.
    """

    def test_malformed_start_date_does_not_cause_500(
        self, logged_in_client
    ):
        """A non-date string in start_date must not produce a server error."""
        response = logged_in_client.get('/profile', query_string={
            'start_date': 'not-a-date',
        })
        assert response.status_code != 500

    def test_malformed_end_date_does_not_cause_500(
        self, logged_in_client
    ):
        """A non-date string in end_date must not produce a server error."""
        response = logged_in_client.get('/profile', query_string={
            'end_date': 'not-a-date',
        })
        assert response.status_code != 500

    def test_impossible_date_values_do_not_cause_500(
        self, logged_in_client
    ):
        """Out-of-range date values (e.g., month 13) must not produce a server error."""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-13-45',
            'end_date': '2026-99-99',
        })
        assert response.status_code != 500

    def test_unknown_extra_query_params_do_not_cause_500(
        self, logged_in_client
    ):
        """
        Extra query params not understood by the route must be ignored
        and must not break the page.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-01',
            'end_date': '2026-04-30',
            'sort': 'amount',         # not a supported param
            'page': '2',              # not a supported param
        })
        assert response.status_code == 200

    def test_whitespace_only_date_params_treated_as_absent(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        The route strips and falls back to None for blank strings.
        Passing params that contain only whitespace must behave the same as
        passing no filter at all: all expenses shown, no active indicator.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '   ',
            'end_date': '   ',
        })
        assert response.status_code == 200
        # All expenses visible
        assert b'March start' in response.data
        assert b'May start' in response.data
        # No filter indicator shown
        assert b'Showing:' not in response.data


# ------------------------------------------------------------------ #
# Clear button / URL hygiene                                          #
# ------------------------------------------------------------------ #

class TestClearFilterLink:
    """
    The 'Clear' link in the filter form must resolve to /profile with no
    query parameters.  This is verifiable via the HTML href attribute.
    """

    def test_clear_link_href_has_no_query_string(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        When a filter is active the Clear anchor's href must be exactly
        '/profile' with no appended query parameters.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-01',
        })
        html = response.data.decode('utf-8')
        # The href generated by url_for('profile') contains no query params
        assert 'href="/profile"' in html

    def test_clear_link_present_when_filter_applied(
        self, logged_in_client, multi_expense_fixture
    ):
        """The Clear link must be rendered when a filter is active."""
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-01',
        })
        assert b'Clear' in response.data

    def test_clear_link_present_even_when_no_filter_applied(
        self, logged_in_client
    ):
        """
        The filter form (and its Clear link) renders on every profile page
        load, not only when a filter is active.
        """
        response = logged_in_client.get('/profile')
        assert b'Clear' in response.data


# ------------------------------------------------------------------ #
# Filter form structure                                               #
# ------------------------------------------------------------------ #

class TestFilterFormStructure:
    """
    Verify that the filter form elements required by the specification
    are present in the rendered HTML.
    """

    def test_filter_form_uses_get_method(self, logged_in_client):
        """Filter form method must be GET so params are preserved in the URL."""
        response = logged_in_client.get('/profile')
        html = response.data.decode('utf-8')
        # The form tag for filterForm must specify method="GET"
        assert 'id="filterForm"' in html
        assert 'method="GET"' in html

    def test_filter_form_has_start_date_input(self, logged_in_client):
        """The filter form must contain an input with name='start_date'."""
        response = logged_in_client.get('/profile')
        assert b'name="start_date"' in response.data

    def test_filter_form_has_end_date_input(self, logged_in_client):
        """The filter form must contain an input with name='end_date'."""
        response = logged_in_client.get('/profile')
        assert b'name="end_date"' in response.data

    def test_filter_form_has_apply_button(self, logged_in_client):
        """The filter form must contain a submit button labelled 'Apply Filter'."""
        response = logged_in_client.get('/profile')
        assert b'Apply Filter' in response.data

    def test_filter_inputs_are_of_type_date(self, logged_in_client):
        """Both filter inputs must be type='date' for browser date-picker support."""
        response = logged_in_client.get('/profile')
        html = response.data.decode('utf-8')
        # Count occurrences of type="date" — expect at least 2 (start and end)
        assert html.count('type="date"') >= 2


# ------------------------------------------------------------------ #
# Invalid range: redirect preserves no stale filter                   #
# ------------------------------------------------------------------ #

class TestInvalidRangeRedirect:
    """
    Additional cases around the start > end validation, checking that the
    redirect destination carries no filter state and that the error message
    is specific enough to guide the user.
    """

    def test_invalid_range_redirect_lands_on_profile(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        After an invalid range rejection the redirect must land on /profile
        (not /login or any other route).
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-12-31',
            'end_date': '2026-01-01',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert response.location.endswith('/profile')

    def test_invalid_range_redirected_page_has_no_active_indicator(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        After following the redirect from an invalid range, the resulting
        page must not display the filter active indicator.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-12-31',
            'end_date': '2026-01-01',
        }, follow_redirects=True)
        assert b'Showing:' not in response.data

    def test_equal_dates_not_rejected_as_invalid_range(
        self, logged_in_client, multi_expense_fixture
    ):
        """
        start_date == end_date is a valid single-day range.
        The route must not flash an error for this case.
        """
        response = logged_in_client.get('/profile', query_string={
            'start_date': '2026-04-15',
            'end_date': '2026-04-15',
        })
        assert response.status_code == 200
        assert b'Start date must be before end date.' not in response.data
