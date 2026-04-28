# Expense Tracker Database Specification

## Overview

This document defines the database schema, relationships, business rules, and implementation requirements for the Expense Tracker application. The application uses SQLite as the database backend with two primary tables: **Users** and **Expenses**.

---

## 1. Database Tables

### 1.1 Users Table

**Table Name:** `users`

**Purpose:** Store user account information and authentication details.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user identifier |
| `name` | TEXT | NOT NULL | User's full name |
| `email` | TEXT | NOT NULL, UNIQUE | User's email address (used for login) |
| `password` | TEXT | NOT NULL | Hashed password (using secure hashing algorithm) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

**Indexes:**
- Primary Key on `id`
- Unique Index on `email` (for fast login lookups)

---

### 1.2 Expenses Table

**Table Name:** `expenses`

**Purpose:** Store individual expense records linked to users.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique expense identifier |
| `user_id` | INTEGER | NOT NULL, FOREIGN KEY → users(id) | Reference to user who created the expense |
| `amount` | DECIMAL(10, 2) | NOT NULL, CHECK(amount > 0) | Expense amount in INR (positive numbers only) |
| `category` | TEXT | NOT NULL, DEFAULT 'Others' | Expense category (predefined list) |
| `date` | DATE | NOT NULL | Date of the expense |
| `description` | TEXT | | Optional description of the expense (max 500 chars) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp when expense was recorded |

**Indexes:**
- Primary Key on `id`
- Foreign Key on `user_id` (with CASCADE delete)
- Index on `user_id` (for fast user expense lookups)
- Index on `date` (for filtering by date range)

---

## 2. Expense Categories

**Predefined Categories:**

1. `Food` - Groceries, dining, meals
2. `Transport` - Gas, public transport, vehicle maintenance
3. `Bills` - Utilities, rent, subscriptions
4. `Health` - Medical, healthcare, medicines
5. `Entertainment` - Movies, gaming, hobbies
6. `Shopping` - Clothing, groceries, general shopping
7. `Others` - Miscellaneous expenses

**Validation Rule:** Only these seven categories are allowed. Any attempt to insert an invalid category should be rejected with an error.

---

## 3. Database Relationships

### Foreign Key Constraint

```
expenses.user_id → users.id
```

**Referential Integrity Rules:**
- **ON DELETE:** CASCADE - When a user is deleted, all their expenses are deleted automatically
- **ON UPDATE:** CASCADE - When a user ID is updated, all related expenses are updated
- **FOREIGN KEY CONSTRAINTS:** Enabled by default in database/db.py

---

## 4. Business Rules

1. **Email Uniqueness:** Each user must have a unique email address (case-insensitive recommended in validation)

2. **Password Security:** 
   - Passwords must be hashed using a secure algorithm (e.g., werkzeug.security or bcrypt)
   - Raw passwords should never be stored in the database

3. **Amount Validation:**
   - Expense amounts must be positive numbers (> 0)
   - Amounts should support decimals up to 2 decimal places (INR standard)
   - Only INR currency is supported (no multi-currency)

4. **Date Validation:**
   - Expense date cannot be in the future
   - Expense date should be reasonable (not more than 10 years in the past)

5. **Description:**
   - Optional field
   - Maximum 500 characters if provided
   - Can be empty or NULL

6. **Timestamps:**
   - `created_at` is auto-generated and immutable
   - Both tables use CURRENT_TIMESTAMP (UTC recommended)

7. **User Access Control:**
   - Users should only see/edit/delete their own expenses
   - No cross-user expense access

---

## 5. Seed Data

### Purpose
Provide initial test data for development and demonstration.

### Users Seed Data

```
1. Name: "John Doe"
   Email: "john@example.com"
   Password: "password123" (hashed)

2. Name: "Jane Smith"
   Email: "jane@example.com"
   Password: "password456" (hashed)
```

### Expenses Seed Data (Sample for each category)

For **John Doe** (user_id: 1):
- Food: ₹500, Date: 2026-04-20, Description: "Weekly groceries"
- Transport: ₹150, Date: 2026-04-22, Description: "Uber ride to office"
- Bills: ₹2000, Date: 2026-04-01, Description: "Electricity bill"
- Health: ₹800, Date: 2026-04-15, Description: "Doctor visit"
- Entertainment: ₹300, Date: 2026-04-25, Description: "Movie tickets"
- Shopping: ₹1200, Date: 2026-04-18, Description: "New t-shirts"
- Others: ₹100, Date: 2026-04-26, Description: "Miscellaneous"

For **Jane Smith** (user_id: 2):
- Food: ₹600, Date: 2026-04-21, Description: "Lunch meeting"
- Transport: ₹200, Date: 2026-04-23, Description: "Cab ride"
- Bills: ₹1500, Date: 2026-04-05, Description: "Internet bill"
- Health: ₹400, Date: 2026-04-10, Description: "Pharmacy"
- Entertainment: ₹500, Date: 2026-04-24, Description: "Concert tickets"
- Shopping: ₹2500, Date: 2026-04-19, Description: "Formal dress"
- Others: ₹50, Date: 2026-04-27, Description: "Parking"

---

## 6. Error Handling Strategy

### Database-Level Errors

| Error Type | Trigger | Handling |
|-----------|---------|----------|
| UNIQUE Constraint | Duplicate email on user registration | Return 409 Conflict with message: "Email already registered" |
| FOREIGN KEY Constraint | Invalid user_id in expense insert | Return 400 Bad Request with message: "User not found" |
| CHECK Constraint (amount > 0) | Negative or zero amount | Return 400 Bad Request with message: "Amount must be greater than zero" |
| NOT NULL Constraint | Missing required field | Return 400 Bad Request with message: "Required field missing: [field_name]" |
| Invalid Category | Category not in predefined list | Return 400 Bad Request with message: "Invalid category. Allowed: Food, Transport, Bills, Health, Entertainment, Shopping, Others" |

### Application-Level Errors

1. **Database Connection Errors:** Log to server logs, return 500 Internal Server Error
2. **Transaction Rollback:** Catch exceptions, rollback transaction, return appropriate error response
3. **Date Validation:** Validate on application layer before insert
4. **Email Format Validation:** Validate email format before insert

### Error Response Format

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

---

## 7. Database Connection & Integration

### Connection Management

**File:** `database/db.py`

**Functions to Implement:**

1. **`get_db()`**
   - Opens SQLite connection
   - Enables foreign key constraints
   - Sets row_factory to sqlite3.Row for dict-like access
   - Returns connection object

2. **`init_db()`**
   - Creates both tables if they don't exist
   - Sets up indexes
   - Enables foreign key constraints
   - Called once during app initialization

3. **`seed_db()`**
   - Clears existing data (optional, with confirmation)
   - Inserts seed data
   - Called manually for development/testing

### app.py Integration Points

1. **Import:** `from database.db import get_db, init_db, seed_db`

2. **Initialization:** Call `init_db()` on first app load or in a setup route

3. **Route Usage:** Use `get_db()` in route handlers to query/insert/update/delete data

4. **Example Pattern:**
   ```python
   @app.route('/expenses', methods=['POST'])
   def add_expense():
       db = get_db()
       # Validate input
       # Insert into expenses table
       # Return response
   ```

---

## 8. SQLite Configuration

### Database File Location
- **Path:** `instance/expense_tracker.db` (or `instance.db`)
- **Version:** SQLite 3
- **Timeout:** 5 seconds (for connection wait)

### Pragma Statements

```sql
PRAGMA foreign_keys = ON;        -- Enable foreign key constraints
PRAGMA journal_mode = WAL;       -- Write-Ahead Logging for concurrency
PRAGMA synchronous = NORMAL;     -- Balance between speed and safety
```

### CREATE TABLE Statements

**Users Table:**
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Expenses Table:**
```sql
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK(amount > 0),
    category TEXT NOT NULL DEFAULT 'Others',
    date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
```

---

## 9. app.py Modifications

### Changes Required

1. **Add database initialization on app startup**
   ```python
   # In app creation or @app.before_first_request
   init_db()
   ```

2. **Add route for seeding data (dev only)**
   ```python
   @app.route('/admin/seed', methods=['POST'])
   def seed_database():
       # Only allow in development
       # Call seed_db()
   ```

3. **Update login route to query users table**
   ```python
   @app.route('/login', methods=['POST'])
   def login():
       # Verify email/password against users table
   ```

4. **Update register route to insert into users table**
   ```python
   @app.route('/register', methods=['POST'])
   def register():
       # Insert new user into users table
   ```

5. **Implement expense management routes**
   ```python
   @app.route('/expenses', methods=['GET'])          # List user's expenses
   @app.route('/expenses', methods=['POST'])         # Add expense
   @app.route('/expenses/<int:id>/edit', methods=['POST'])  # Edit expense
   @app.route('/expenses/<int:id>/delete', methods=['POST'])  # Delete expense
   ```

6. **Add error handling middleware**
   ```python
   @app.errorhandler(400)
   @app.errorhandler(409)
   @app.errorhandler(500)
   # Custom error handlers
   ```

---

## 10. Definition of Done

### Phase 1: Database Setup (database/db.py)

- [ ] `get_db()` function opens SQLite connection with proper configuration
- [ ] `init_db()` creates users and expenses tables with all columns and constraints
- [ ] All indexes are created for performance optimization
- [ ] Foreign key constraints are properly configured with CASCADE
- [ ] `seed_db()` inserts sample data for both users and expenses
- [ ] All PRAGMA statements are set correctly
- [ ] Database file path is correctly configured in `.gitignore`
- [ ] Error handling for database operations is in place

### Phase 2: app.py Integration

- [ ] `init_db()` is called on app startup
- [ ] Authentication routes (login/register) use database
- [ ] User sessions/authentication is implemented
- [ ] All expense routes (CRUD operations) are implemented
- [ ] Proper error responses are returned for validation failures
- [ ] Access control ensures users only see their own expenses

### Phase 3: Testing & Validation

- [ ] All database operations have been tested manually
- [ ] Seed data is correctly inserted and accessible
- [ ] Foreign key constraints are working (deleting user deletes expenses)
- [ ] Category validation is enforced
- [ ] Amount validation (> 0) is enforced
- [ ] Email uniqueness constraint works
- [ ] Password hashing is implemented
- [ ] All error cases return appropriate error responses

### Phase 4: Documentation

- [ ] Database schema is documented
- [ ] API endpoints are documented
- [ ] Setup instructions are clear in CLAUDE.md
- [ ] Error codes and messages are documented
- [ ] Seed data initialization is documented

---

## 11. Testing Considerations

### Manual Testing Checklist

1. **User Registration**
   - [ ] Duplicate email rejection
   - [ ] Valid user creation
   - [ ] Password hashing verification

2. **User Login**
   - [ ] Valid credentials acceptance
   - [ ] Invalid credentials rejection
   - [ ] Session management

3. **Expense Operations**
   - [ ] Add expense with all categories
   - [ ] Invalid category rejection
   - [ ] Negative amount rejection
   - [ ] Future date validation
   - [ ] Edit own expenses only
   - [ ] Delete own expenses only
   - [ ] List only user's expenses

4. **Database Integrity**
   - [ ] Cascade delete on user deletion
   - [ ] Foreign key constraint enforcement
   - [ ] Unique email constraint enforcement

---

## 12. Security Considerations

1. **Password Storage:**
   - Use werkzeug.security `generate_password_hash()` and `check_password_hash()`
   - Never store plain text passwords

2. **SQL Injection Prevention:**
   - Always use parameterized queries with `?` placeholders
   - Never concatenate user input into SQL strings

3. **User Access Control:**
   - Verify user session/authentication before accessing expenses
   - Query expenses with WHERE user_id = current_user.id

4. **Input Validation:**
   - Validate email format
   - Validate amount is positive decimal
   - Validate date is not in future
   - Validate description length

---

## 13. Future Enhancements (Out of Scope)

- Multi-currency support
- Recurring expenses
- Budget tracking and alerts
- Expense tags and custom categories
- Data export (CSV, PDF)
- Charts and analytics
- Mobile app
- Cloud database migration

---

## Review Checklist for Approval

- [ ] Schema design is approved
- [ ] Business rules are clear and acceptable
- [ ] Error handling strategy is adequate
- [ ] Seed data is sufficient for testing
- [ ] app.py integration points are understood
- [ ] Definition of Done is realistic
- [ ] No questions about database relationships

---

**Document Version:** 1.0  
**Last Updated:** 2026-04-28  
**Created By:** Claude Code  
**Status:** Ready for Review
