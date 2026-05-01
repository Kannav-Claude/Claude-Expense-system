# Step 01: Registration

## Overview
The Registration feature allows new users to create accounts in the Expense Tracker application. This is a foundational feature that enables user authentication and account management. Users will be able to sign up with their name, email, and password, establishing the basis for personalized expense tracking.

## Feature Requirements
- Users can create a new account with name, email, and password
- Email addresses must be unique across the system
- Passwords must be at least 8 characters long
- Passwords must be securely hashed before storage
- Form validation provides immediate feedback on errors
- Users are directed to login after successful registration
- Clear error messages for duplicate emails, missing fields, or weak passwords

## Routes to Implement

### POST /register
- **Method:** GET, POST
- **Parameters (POST):**
  - `name` (string) - User's full name (required)
  - `email` (string) - User's email address (required, unique)
  - `password` (string) - User's password (required)
- **Response (GET):** Registration form template
- **Response (POST - Success):** Redirect to `/login` with success flash message
- **Response (POST - Error):** Return registration form with error flash message
- **Status Codes:** 200 (form display), 302 (redirect), 400 (validation error)

## Database Changes

### New Tables
**users table:**
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT) - Unique user identifier
- `name` (TEXT NOT NULL) - User's full name
- `email` (TEXT NOT NULL UNIQUE) - User's email (must be unique)
- `password` (TEXT NOT NULL) - Hashed password
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP) - Account creation timestamp

### Constraints
- Email must be unique (prevents duplicate accounts)
- All fields are required for account creation

## Frontend Components

### New Templates
**register.html**
- Inherits from `base.html` for consistent styling
- Form with fields: name, email, password
- Submit button labeled "Create Account"
- Link to login page for existing users
- Flash messages for success/error feedback
- Basic form validation (HTML5)

### Form Validation (Client-Side)
- All fields marked as required
- Email field uses HTML5 email validation
- Password field type for security

### User Feedback
- Success message: "Account created. Please log in."
- Error messages:
  - "All fields are required."
  - "Email already registered."
  - "Password must be at least 8 characters long."

## Testing Strategy

### Unit Tests
- Test registration route GET request returns form
- Test registration with valid data creates account and redirects
- Test registration with duplicate email shows error
- Test registration with missing fields shows error
- Test password is hashed (not stored as plaintext)

### Integration Tests
- Test full registration flow from form submission to database
- Test user can login after registration
- Test email uniqueness constraint at database level

### Edge Cases
- Empty strings in required fields
- Whitespace-only entries
- Mixed case email handling (stored as lowercase)
- Very long names or emails
- Special characters in inputs

### Test Data Requirements
- Sample user data for registration attempts
- Duplicate email test case
- Various validation error scenarios

## Implementation Checklist
- [ ] Users table created in database
- [ ] Password hashing configured with werkzeug
- [ ] GET /register route returns registration form
- [ ] POST /register route processes form submission
- [ ] Email uniqueness constraint enforced
- [ ] Password length validation (minimum 8 characters)
- [ ] Form validation implemented
- [ ] Error/success flash messages configured
- [ ] register.html template created
- [ ] Tests written for all scenarios
- [ ] Code reviewed for security (SQL injection, password handling)
- [ ] Feature merged to main

## Clarifying Questions (Answered)

1. **Password Requirements:** ✅ Minimum 8 characters - passwords must be at least 8 characters long.

2. **Terms & Conditions:** ✅ No - T&Cs acceptance not required during registration.

3. **Name Field:** ✅ Single full name - one field for complete name (no first/last split).

4. **Redirect After Registration:** ✅ Direct to login - newly registered users redirected immediately to login page.

5. **Error Messages:** Keep messages consistent - "Email already registered." for duplicates, "All fields are required." for missing fields.

6. **Email Validation:** HTML5 validation only - no confirmation emails required at this step.

## Dependencies
- Database initialization (database/db.py must be set up)
- Flask framework with session management
- werkzeug.security for password hashing
- Base template (base.html) for consistent styling
- Flash messaging system in Flask

## Notes

### Design Decisions
- **Password Hashing:** Uses werkzeug's `generate_password_hash()` with default PBKDF2 algorithm for security
- **Email Uniqueness:** Database constraint (UNIQUE) prevents duplicate emails at the database level
- **Email Normalization:** Email is converted to lowercase to handle case-insensitive lookups consistently
- **Post-Registration Flow:** Users are redirected to login to confirm email/password combination works

### Considerations
- Passwords are never logged or displayed in error messages
- Email addresses are stored in lowercase for consistency
- User names are trimmed of leading/trailing whitespace
- Flask session is used for post-login persistence

### Known Constraints
- No email confirmation required (assumes trusted user input)
- No password strength requirements enforced (can be added in future steps)
- No captcha or rate limiting (can be added for production)
- SQLite database has limits for high-scale applications
