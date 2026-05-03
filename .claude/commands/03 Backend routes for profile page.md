# Step 03: Backend Routes for Profile Page

## Overview
This step implements the backend routes and database support for a user profile page where authenticated users can view and manage their account information. The profile page allows users to see their current details (name, email) and optionally update their information (name, password). This is essential for users to maintain control over their accounts and core functionality of the application. Remove all hardcoded data and show only the data for the logged user. Use the existing design but have basic charts and data points for the logged user

## Feature Requirements
- **View Profile:** Display current user's name and email in a read-only or editable format
- **Edit Profile:** Allow users to update their name and optionally change their password
- **Security:** Validate password changes with minimum length requirements (consistent with registration)
- **User Feedback:** Clear flash messages for success/error states
- **Authentication:** Only logged-in users can access the profile page

## Routes to Implement

### GET /profile
- **Purpose:** Display the user's profile page
- **Authentication:** Required (redirect to login if not authenticated)
- **Request Parameters:** None
- **Response:** Rendered `profile.html` template with user data
- **Status Code:** 200 (success) or 302 (redirect to login if unauthenticated)
- **Data Passed:** User object with id, name, email, created_at

### POST /profile
- **Purpose:** Update user profile information
- **Authentication:** Required (redirect to login if not authenticated)
- **Request Parameters:**
  - `name` (optional): New name for the user
  - `password` (optional): New password (if provided, triggers password change)
  - `password_confirm` (optional): Password confirmation for validation
- **Validation Rules:**
  - Name: Must not be empty if provided
  - Password: Minimum 8 characters if provided
  - Password confirmation must match the new password
  - At least one field (name or password) should be updated
- **Response:** Redirect to `/profile` on success with success flash message
- **Status Code:** 200 (reload with validation errors) or 302 (redirect on success)
- **Error Handling:** Flash messages for validation errors, database errors

## Database Changes

### Users Table Modifications
No new tables needed. The existing `users` table is sufficient:
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT NOT NULL)
- `email` (TEXT NOT NULL UNIQUE)
- `password` (TEXT NOT NULL)
- `created_at` (TIMESTAMP)

The `email` field is intentionally read-only to simplify implementation and maintain account integrity.

## Frontend Components

### New Templates
- **profile.html**: Display user profile with edit functionality
  - Show current name and email
  - Form fields for updating name
  - Form fields for password change (with confirmation)
  - Submit button for updates
  - Inherit from base.html for consistent navigation

### Form Validation (JavaScript)
- Client-side validation for password length (at least 8 characters)
- Client-side validation for password confirmation matching
- Provide immediate feedback on form changes

### User Feedback
- Success message: "Profile updated successfully."
- Error messages for:
  - "Name cannot be empty."
  - "Password must be at least 8 characters long."
  - "Passwords do not match."
  - "Failed to update profile."
  - "No changes made."

## Testing Strategy

### Unit Tests
- Test that unauthenticated users are redirected to login
- Test GET /profile returns user data correctly
- Test POST /profile with valid name update
- Test POST /profile with valid password change
- Test POST /profile with password and name change simultaneously

### Validation Tests
- Password minimum length validation (< 8 characters should fail)
- Password confirmation mismatch should fail
- Empty name submission should fail
- No fields provided (name and password both empty) should fail

### Edge Cases
- User manually deletes their own session while on profile page
- Database errors during update (simulate constraint violations)
- Verify password hashing works correctly
- Verify user cannot change other users' profiles (authorization)

### Test Data Requirements
- Existing user fixture from registration tests
- Sample user with known credentials for login

## Implementation Checklist
- [ ] Create GET /profile route with authentication check
- [ ] Create POST /profile route with validation logic
- [ ] Hash password using werkzeug.security when updating
- [ ] Query database to fetch current user info
- [ ] Update user name and/or password in database
- [ ] Create profile.html template
- [ ] Add form validation (client-side JavaScript)
- [ ] Add success/error flash messages
- [ ] Write route tests (authenticated and unauthenticated)
- [ ] Write validation tests
- [ ] Write edge case tests
- [ ] Test password hashing works correctly

## Clarifying Questions

Before implementation, please clarify:

1. **Email Update:** Should users be able to change their email address? (Currently spec keeps email read-only for simplicity.)

2. **Password Confirmation:** Should the current password be required to change the password (for security)?

3. **Profile Fields:** Should the profile include additional fields like:
   - Bio/Description
   - Profile picture
   - Phone number
   - Date of birth

4. **Account Deletion:** Should there be an option to delete the account?

5. **Updated Timestamp:** Should we track when the profile was last updated?

## Dependencies
- **Step 01:** Registration (users table and password hashing)
- **Step 02:** Login and Logout (session management and authentication)
- Existing **base.html** template for consistency

## Notes
- Password updates should use werkzeug's `generate_password_hash()` for security
- The profile page requires authentication, following the same pattern as `/expenses` route
- Database operations follow established patterns: parameterized queries, transaction handling, try-finally for connection closure
- Flash messages follow the same pattern as existing routes (success/error)
- Email field remains read-only to avoid complexity of email verification/uniqueness during update
- No changes to existing users table schema required
