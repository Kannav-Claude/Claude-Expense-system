# 04: Date Filter on the Profile Page

## Overview

Add date range filtering capability to the profile page's expense list, allowing users to view expenses within a specific date range. Currently, the profile page displays all expenses sorted chronologically. This feature will enable users to narrow down their expense view by selecting a start and end date, making it easier to analyze spending patterns for specific periods (e.g., monthly, quarterly, or custom date ranges).

**Why it's important:**
- Users can analyze spending by custom time periods
- Reduces cognitive load when reviewing large expense lists
- Supports financial planning and expense tracking workflows

**How it fits:**
The profile page already displays a spending summary (total spent, expense count, average expense) and an expense list. The date filter will refine what expenses are included in both the list display and potentially the statistics.

---

## Feature Requirements

### Primary Objectives
1. Allow users to filter expenses by a date range (start date and end date)
2. Show filtered results in the expense table on the profile page
3. Maintain existing functionality (account info, spending summary stats)
4. Provide clear visual feedback when a filter is applied

### User Interactions
- User navigates to `/profile`
- User sees the current "Expenses by Date" section with all expenses
- User can input a start date and end date in filter controls
- User clicks "Apply Filter" button
- Expense list updates to show only expenses within the date range
- User can clear the filter to see all expenses again
- Stats (total spent, expense count, average) update to reflect filtered data

### Expected Outcomes
- Expense table displays only expenses within the selected date range
- Filter state is preserved during the page session (optional: could be persisted in localStorage)
- Clear feedback if no expenses match the filter criteria
- Stats reflect the filtered data

---

## Routes to Implement

### Modified Route: `/profile` (GET)
**Current behavior:** Fetches all expenses for the user

**New behavior:** 
- Accept optional query parameters for date filtering
  - `start_date`: ISO format date (YYYY-MM-DD)
  - `end_date`: ISO format date (YYYY-MM-DD)
- If both parameters present, filter expenses to that range
- If only one parameter present, use it as inclusive boundary
- If neither present, show all expenses (current behavior)
- **Validation:** If start_date > end_date, reject with error flash message

**Request parameters:**
```
GET /profile?start_date=2026-04-01&end_date=2026-04-30
GET /profile?start_date=2026-04-01  (from start_date onwards)
GET /profile?end_date=2026-04-30    (up to end_date)
GET /profile                         (all expenses)
```

**Response structure:**
```python
{
    'user': {...},
    'stats': {
        'expense_count': int,      # Reflects filtered data if filter applied
        'total_spent': float,      # Reflects filtered data if filter applied
        'avg_expense': float       # Reflects filtered data if filter applied
    },
    'expense_list': [
        {'id': int, 'date': str, 'category': str, 'amount': float, 'description': str},
        ...
    ],
    'filter_applied': bool,
    'start_date': str or None,
    'end_date': str or None
}
```

**Status codes:**
- 200: Success (with or without filter)
- 302: Redirect to login if not authenticated

**Error handling:**
- If start_date > end_date: Flash error message "Start date must be before end date" and re-render with filter form

---

## Database Changes

**No database schema changes required.** The filtering is performed in-memory via SQL WHERE clauses.

**SQL Query modification:**
Current query:
```sql
SELECT id, date, category, amount, description
FROM expenses WHERE user_id = ?
ORDER BY date ASC
```

New query (with date filtering):
```sql
SELECT id, date, category, amount, description
FROM expenses 
WHERE user_id = ? 
  AND (date BETWEEN ? AND ? OR date >= ? OR date <= ?)
ORDER BY date ASC
```

**Index consideration:**
- Existing index `idx_expenses_date` supports efficient date range queries
- No new indexes needed

---

## Frontend Components

### New Elements in `profile.html`
1. **Date Filter Card** (above the expense table)
   - Two date input fields: "From Date" and "To Date"
   - "Apply Filter" button
   - "Clear Filter" button
   - Visual indicator showing if a filter is active

### HTML Structure
```html
<!-- Filter Form Card -->
<div class="profile-card">
    <div class="profile-card-header">Filter Expenses</div>
    <form method="GET" action="{{ url_for('profile') }}" class="filter-form">
        <div class="filter-inputs">
            <div class="form-group">
                <label for="start_date">From Date</label>
                <input type="date" id="start_date" name="start_date" 
                       value="{{ start_date or '' }}" class="form-input">
            </div>
            <div class="form-group">
                <label for="end_date">To Date</label>
                <input type="date" id="end_date" name="end_date" 
                       value="{{ end_date or '' }}" class="form-input">
            </div>
        </div>
        <div class="filter-actions">
            <button type="submit" class="btn-submit">Apply Filter</button>
            <a href="{{ url_for('profile') }}" class="btn-secondary">Clear Filter</a>
        </div>
        {% if filter_applied %}
        <div class="filter-active-indicator">
            Filter applied: {{ start_date or 'Beginning' }} to {{ end_date or 'Today' }}
        </div>
        {% endif %}
    </form>
</div>

<!-- Updated Expenses by Date Section with Empty State -->
{% if expense_list %}
<div class="profile-card">
    <div class="profile-card-header">Expenses by Date</div>
    <div class="expenses-table-wrapper">
        <table class="expenses-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Category</th>
                    <th>Description</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                {% for expense in expense_list %}
                <tr>
                    <td class="expense-date">{{ expense['date'] }}</td>
                    <td class="expense-category">{{ expense['category'] }}</td>
                    <td class="expense-description">{{ expense['description'] or '—' }}</td>
                    <td class="expense-amount">₹{{ "%.2f"|format(expense['amount']) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% else %}
<div class="profile-card profile-empty">
    <p>No expenses found{% if filter_applied %} for the selected date range{% endif %}. 
       {% if not filter_applied %}<a href="{{ url_for('add_expense') }}">Add your first expense.</a>{% endif %}
    </p>
</div>
{% endif %}
```

### CSS Styling (additions to `static/css/style.css`)
```css
.filter-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.filter-inputs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.filter-actions {
    display: flex;
    gap: 0.5rem;
}

.btn-secondary {
    padding: 0.5rem 1rem;
    background-color: #e0e0e0;
    color: #333;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
}

.btn-secondary:hover {
    background-color: #d0d0d0;
}

.filter-active-indicator {
    padding: 0.5rem;
    background-color: #e3f2fd;
    color: #1565c0;
    border-left: 4px solid #1565c0;
    border-radius: 4px;
    font-size: 0.9rem;
}
```

### JavaScript (optional enhancements in `static/js/main.js`)
- Client-side validation to ensure start_date <= end_date
- Prevent submitting invalid date ranges
- Optional: Preserve filter state in localStorage

```javascript
document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.querySelector('.filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            const startDate = document.getElementById('start_date').value;
            const endDate = document.getElementById('end_date').value;
            
            if (startDate && endDate && startDate > endDate) {
                e.preventDefault();
                alert('Start date must be before or equal to end date.');
            }
        });
    }
});
```

---

## Testing Strategy

### Unit Tests (backend)
```python
# Test date range filtering logic
def test_profile_with_date_filter():
    # Setup: seed database with expenses on known dates
    # Assert: returned expenses are within the date range
    
def test_profile_filter_start_date_only():
    # Filter with only start_date
    # Assert: all expenses >= start_date
    
def test_profile_filter_end_date_only():
    # Filter with only end_date
    # Assert: all expenses <= end_date
    
def test_profile_filter_invalid_range():
    # start_date > end_date
    # Assert: handled gracefully (could show all or validate frontend)
    
def test_profile_filter_no_results():
    # Date range with no matching expenses
    # Assert: empty expense list, appropriate message shown
```

### Integration Tests
```python
def test_profile_filter_form_submission():
    # Submit filter form with valid dates
    # Assert: page reloads with filtered data
    
def test_profile_filter_clear():
    # Click "Clear Filter" button
    # Assert: all expenses shown again
```

### Edge Cases
- Start date same as end date (should include that day)
- No expenses in date range (show empty state)
- Future dates (should not appear, but handle gracefully)
- Invalid date formats (browser validation handles this)
- Boundary dates (first and last days of expense history)

### Test Data Requirements
- Expenses spread across multiple dates (April 2026 based on current seed data)
- Mix of expenses with and without descriptions
- Multiple categories represented

---

## Implementation Checklist

- [ ] Modify `/profile` route to accept and process `start_date` and `end_date` query parameters
- [ ] Update SQL query to filter expenses by date range
- [ ] Update stats calculation to use filtered expense data
- [ ] Pass filter state to template (`filter_applied`, `start_date`, `end_date`)
- [ ] Add date filter form to `profile.html` above expense table
- [ ] Add CSS styling for filter form and active indicator
- [ ] Add client-side validation in `main.js`
- [ ] Update "Expenses by Date" heading to indicate filtered state if applicable
- [ ] Write unit tests for date range filtering logic
- [ ] Write integration tests for form submission and clearing
- [ ] Test edge cases (no results, boundary dates, etc.)
- [ ] Code review and feedback
- [ ] Merged to main

---

## Design Decisions (Finalized)

Based on your input, here are the confirmed decisions for this feature:

1. **Stats behavior with filters:** ✅ Stats update to reflect filtered data
   - Total Spent, Expense Count, and Average Expense will recalculate to show only expenses in the selected date range
   - This provides better insights for analyzing spending by period

2. **Filter state persistence:** ✅ Preserve in URL query params only
   - Filters are maintained in the URL (e.g., `?start_date=2026-04-01&end_date=2026-04-30`)
   - Page refresh keeps the filter active
   - Closing the browser or navigating away removes the filter
   - No localStorage persistence

3. **Empty state messaging:** ✅ Empty table with message
   - Show the table structure with a "No expenses found for the selected date range" message
   - Maintain consistent UI layout

4. **Date validation:** ✅ Reject with error message for invalid ranges
   - If start_date > end_date, show a user-friendly error message
   - Backend will flash an error and re-render the page with the filter form
   - User must correct the dates before filtering

---

## Dependencies

### Related Features
- Step 02: Login and Logout (authentication)
- Step 03: Backend Routes for Profile Page (existing profile functionality)

### External Dependencies
- None (uses existing libraries: Flask, SQLite)

### Blocking Factors
- None; can be implemented independently

---

## Notes

### Design Decisions
- **GET method for filtering:** Uses query parameters so filters can be bookmarked and shared
- **Client-side + server-side validation:** Date validation happens on both frontend (browser) and backend for robustness
- **No database changes:** Filtering is done in-memory via SQL WHERE clauses; preserves existing schema

### Considerations
- **Performance:** With proper indexing on `date` column, range queries are efficient even with large expense datasets
- **User experience:** Clear visual feedback about active filters prevents confusion
- **Accessibility:** Date inputs are semantic HTML5, with proper labels for screen readers

### Known Constraints
- Date format is ISO (YYYY-MM-DD) to match HTML5 date input standard
- Only supports contiguous date ranges (no "exclude weekends" or similar complex filtering)
- Expenses are always sorted by date ascending; additional sorting not in this step
