# Step 02: Login and Logout

## Overview
Login and Logout are the core authentication features that allow registered users to access their personal expense data securely. The login flow authenticates users by verifying their email and password, creating a session. The logout flow clears the session, ensuring users are properly signed out. These features are essential for maintaining user privacy and preventing unauthorized access to expense data.

**Why it's important:**
- Enables secure access control to user-specific resources
- Maintains session state across requests
- Protects sensitive financial data through authentication
- Provides a foundation for all authenticated routes in the application

**How it fits into the application:**
- Step 01: Registration creates user accounts with hashed passwords
- Step 02: Login & Logout enables users to authenticate and access their data
- Step 03+: All subsequent features (expenses, profile, etc.) depend on authentication

---

## Feature Requirements

### Login Requirements
- **Primary objectives:**
  - Allow registered users to authenticate with valid email and password
  - Create a session upon successful authentication
  - Display error messages for invalid credentials
  - Redirect authenticated users to their expense dashboard

- **User interactions:**
  - User fills out email and password form on /login page
  - System validates credentials against database
  - On success: session is created, user redirected to /expenses
  - On failure: error message displayed, form remains on same page

- **Expected outcomes:**
  - Valid credentials → Session created + Redirect to /expenses
  - Invalid credentials → Error message "Invalid email or password."
  - Already logged in user accessing /login → May redirect to /expenses (optional)

### Logout Requirements
- **Primary objectives:**
  - Securely clear user session
  - Redirect user to landing page
  - Prevent access to authenticated routes after logout

- **User interactions:**
  - User clicks logout link/button in navigation
  - System clears all session data
  - User is redirected to landing page
  - Subsequent attempts to access /expenses redirect to /login

- **Expected outcomes:**
  - Session cleared successfully
  - User returned to public pages
  - Protected routes are inaccessible without new login

---

## Routes to Implement

### GET /login
- **Purpose:** Display login form to user
- **Response:** Render `login.html` template
- **Status Code:** 200 OK

### POST /login
- **Purpose:** Process login credentials and create session
- **Request Parameters:**
  - `email` (string, required): User's email address
  - `password` (string, required): User's password
  
- **Response:**
  - Success: Redirect to `/expenses` (HTTP 302)
  - Failure: Render `login.html` with error flash message
  
- **Status Codes:**
  - 200 OK (on validation failure, re-render form)
  - 302 Found (on successful authentication)

### GET /logout
- **Purpose:** Clear session and redirect to landing page
- **Response:** Redirect to `/` (HTTP 302)
- **Status Code:** 302 Found
- **Session:** Clears all session data before redirect

---

## Database Changes

### No New Tables Required
Login and logout use the existing `users` table created in Step 01.

### Required User Table Schema (Review from Step 01)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Key Constraints:
- `email` column must be UNIQUE to prevent duplicate registrations
- `password` column must store hashed passwords (using werkzeug.security)
- Foreign key constraints enabled for data integrity

---

## Frontend Components

### Templates Required

#### login.html
- **Purpose:** Display login form and handle user authentication
- **Form Fields:**
  - Email input field (type="email", required)
  - Password input field (type="password", required)
  - Submit button
  
- **Features:**
  - Display flash messages for errors
  - Form validation (client-side: required fields)
  - Link to registration page for new users
  - Link to landing page
  
- **Inherits from:** `base.html` for consistent navigation

#### Modifications to base.html
- **Navigation updates:**
  - Hide login/register links when user is logged in
  - Show logout link when user is logged in
  - Display user's name when authenticated
  
- **User greeting:** "Welcome, {user_name}" or similar

### JavaScript Functionality
- **Client-side validation:**
  - Ensure email field is not empty
  - Ensure password field is not empty
  - Basic email format validation (optional enhancement)

- **User experience enhancements:**
  - Clear password field on page load (security best practice)
  - Disable submit button while form is submitting (optional)
  - Show/hide password toggle (optional enhancement)

### Form Validation
- **Client-side:**
  - Required field validation
  - Email format validation

- **Server-side (app.py):**
  - Email existence check in database
  - Password verification using `check_password_hash()`
  - Case-insensitive email handling

### User Feedback
- **Error messages:**
  - "Invalid email or password." (for non-matching credentials or missing email)
  - Flash messages displayed at top of form
  
- **Success feedback:**
  - Automatic redirect to /expenses dashboard
  - Session created with user_id and user_name

---

## Testing Strategy

### Unit Tests
- **Test valid login:** Correct email + password → Session created
- **Test invalid email:** Non-existent email → Error message displayed
- **Test invalid password:** Correct email + wrong password → Error message
- **Test missing fields:** Empty email or password → Validation error
- **Test case-insensitive email:** Email with uppercase letters should match lowercase in database
- **Test logout:** Session cleared after logout → Redirect to landing

### Integration Tests
- **Login flow:** User registers → Login with new credentials → Access /expenses
- **Logout flow:** Logged-in user → Click logout → Redirected to landing → Cannot access /expenses
- **Session persistence:** After login, session persists across page navigations
- **Protected routes:** Accessing /expenses without login → Redirected to /login

### Edge Cases
- **SQL injection:** Test login with SQL injection attempts (should be prevented by parameterized queries)
- **Password hashing:** Verify passwords are not stored in plain text
- **Case sensitivity:** Email addresses should be case-insensitive
- **Special characters:** Test emails and passwords with special characters
- **Very long inputs:** Test with extremely long email/password values (should be truncated/rejected)
- **Whitespace handling:** Email should be trimmed of whitespace

### Test Data Requirements
- Sample registered user: 
  - Email: `john@example.com`
  - Password: `password123` (hashed with werkzeug)
  - Name: `John Doe`

---

## Implementation Checklist

- [ ] **Login Route (GET)**: Display login.html form
- [ ] **Login Route (POST)**: Validate credentials and create session
  - [ ] Get email and password from form
  - [ ] Query users table with parameterized query
  - [ ] Verify password using check_password_hash()
  - [ ] Create session with user_id and user_name
  - [ ] Flash error message on validation failure
- [ ] **Logout Route**: Clear session and redirect
  - [ ] Call session.clear()
  - [ ] Redirect to landing page
- [ ] **Template (login.html)**: Create form with email and password fields
  - [ ] Display flash messages
  - [ ] Add client-side validation
  - [ ] Style consistently with other pages
- [ ] **Template (base.html)**: Update navigation for authenticated state
  - [ ] Show logout link when logged in
  - [ ] Show user name in navigation
  - [ ] Hide login/register links for authenticated users
- [ ] **Frontend Validation**: Email/password required fields
- [ ] **Tests Written**: Unit and integration tests for all scenarios
- [ ] **Code Review**: Verify password hashing and SQL injection prevention
- [ ] **Merged to main**: Pull request approved and merged

---

## Clarifying Questions

1. **Case Sensitivity for Email:**
   - Should email comparison be case-insensitive? (Recommended: Yes, as per email standards)
   - Should stored emails be normalized to lowercase?

2. **Remember User:**
   - Should there be a "Remember Me" checkbox for persistent login? (Scope for future step)

3. **Password Recovery:**
   - Should there be a "Forgot Password" link on login page? (Scope for future step)

4. **Account Lockout:**
   - Should there be account lockout after N failed login attempts? (Could be added later for security)

5. **Navigation Bar:**
   - Where should the logout button appear in the navigation?
   - What should happen if user tries to access /login while already logged in? (Redirect to /expenses?)

6. **Session Timeout:**
   - Should sessions have an expiration time? (Could be a future enhancement)

7. **Flash Message Duration:**
   - Should error messages auto-dismiss after X seconds? (UI enhancement)

---

## Dependencies

### Related Features
- **Step 01: Registration** (Prerequisite) - Creates user accounts with hashed passwords
- **Step 03: Expenses List** (Dependent) - Protected route that requires login
- **Step 04-06: Expense Management** (Dependent) - All expense routes require authentication

### External Dependencies
- **werkzeug.security** - For password hashing and verification
- **Flask sessions** - For maintaining user state
- **SQLite** - For user data storage

### Blocking Factors
- None - This step can proceed once registration is complete

---

## Notes

### Design Decisions
1. **Email as Primary Identifier:** Users login with email (more intuitive than user ID)
2. **Case-Insensitive Email:** Email handling normalizes to lowercase for consistency
3. **Parameterized Queries:** All database operations use parameterized queries to prevent SQL injection
4. **Session Storage:** Using Flask sessions (server-side storage is safer than JWT tokens for this application)
5. **Password Hashing:** Using werkzeug's `check_password_hash()` instead of plain-text comparison

### Security Considerations
- **Password Security:** Passwords are hashed using PBKDF2 with SHA-256 (werkzeug default)
- **Session Security:** Session uses secure HTTP-only cookies
- **SQL Injection Prevention:** All queries use parameterized queries (?)
- **CSRF Protection:** Form submission should include CSRF token (Flask requirement)
- **Generic Error Messages:** Using "Invalid email or password" prevents account enumeration attacks

### Implementation Patterns
- **Database Connections:** Always use try/finally to ensure connections are closed
- **Flash Messages:** Use category ("error", "success") for styling
- **Redirects:** Use `url_for()` instead of hardcoded URLs for maintainability
- **Template Inheritance:** All templates inherit from `base.html` for consistency

### Known Constraints
- SQLite is used (single-threaded, suitable for development/small deployments)
- No email verification required for account creation (added later if needed)
- No multi-factor authentication in initial implementation
