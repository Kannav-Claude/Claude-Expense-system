# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Expense Tracker** web application built with Flask. The project is structured as an incremental learning application where students implement features across multiple "steps" (database setup, authentication, user profiles, expense management, etc.).

**Tech Stack:**
- Backend: Flask 3.1.3
- Frontend: HTML/CSS/JavaScript (server-rendered templates)
- Database: SQLite
- Testing: pytest + pytest-flask

## Development Setup

**Prerequisites:**
- Python 3.8+ installed
- Virtual environment (`venv/`) should already exist

**Activate the virtual environment:**
```bash
# Windows
source venv/Scripts/activate

# macOS/Linux
source venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

## Common Commands

**Run the development server:**
```bash
python app.py
```
The app runs on `http://localhost:5001` with debug mode enabled (auto-reload on file changes).

**Run tests:**
```bash
pytest
```

**Run a specific test:**
```bash
pytest tests/test_name.py::test_function
```

**Initialize the database:**
```bash
# This function is defined in database/db.py and should be called by students
python -c "from database.db import init_db; init_db()"
```

## Git Workflow

**Committing changes:**
- Use `/git-command` for safely committing folder renames. This command confirms before running, checks for duplicate commit messages, and never pushes automatically.
- For other commits, use standard git commands: `git add`, `git commit`, etc.
- The `/git-command` skill is scoped to add + commit only; push to remote manually when ready.

## Project Structure

```
.
├── app.py                    # Main Flask application with all routes
├── database/                 # Database module (to be implemented)
│   ├── db.py                # Database functions: get_db(), init_db(), seed_db()
│   └── __init__.py           # Package marker
├── templates/                # Jinja2 HTML templates
│   ├── base.html            # Base template with navigation
│   ├── landing.html         # Home page
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── terms.html           # Terms and Conditions
│   └── privacy.html         # Privacy Policy
├── static/                   # Static assets (CSS, JavaScript)
│   ├── css/style.css        # Main stylesheet
│   └── js/main.js           # Client-side JavaScript
├── requirements.txt          # Python dependencies
└── .gitignore               # Ignore venv, database files, etc.
```

## Architecture Notes

**Route Organization:**
All routes are currently defined in `app.py` using decorators. There are three categories:
1. **Implemented routes** (landing, register, login, terms, privacy) - return rendered templates
2. **Placeholder routes** (logout, profile, add_expense, edit_expense, delete_expense) - return placeholder strings to be replaced with full implementations

**Database Layer:**
The `database/db.py` module is a **stub with no implementation**. Students implement these functions during Step 1:
- `get_db()` - Opens SQLite connection with `row_factory` and foreign key constraints enabled
- `init_db()` - Creates all tables using `CREATE TABLE IF NOT EXISTS`
- `seed_db()` - Inserts sample data for development and testing

**Frontend:**
- Templates use Jinja2 syntax and inherit from `base.html` for consistent styling
- Minimal JavaScript in `main.js` includes modal handling for the video player
- CSS in `static/css/style.css` handles layout and styling for all pages

## Key Implementation Patterns

**Template Rendering:**
Routes use `render_template("template_name.html")` to serve HTML. All templates should inherit from `base.html` to maintain consistent navigation and styling.

**Route Parameters:**
Dynamic routes like `/expenses/<int:id>/edit` use URL parameters. The parameter type (e.g., `<int:id>`) ensures type validation in Flask.

**Database Integration:**
When implementing database features, import and use `get_db()` from `database.db` to get a connection. Ensure all database operations use parameterized queries to prevent SQL injection.

## Testing

The project uses pytest with pytest-flask for testing. A `tests/` directory will be created as part of the implementation steps. When tests are added, they should:
- Test individual routes with the Flask test client
- Verify response status codes and returned content
- Mock or use a test database (typically done via fixtures in pytest)

Example test pattern:
```python
def test_landing_route(client):
    response = client.get('/')
    assert response.status_code == 200
```

**Run tests:**
```bash
pytest                                           # Run all tests
pytest tests/test_name.py::test_function        # Run a specific test
```

## Important Notes

- The project is designed for incremental development; placeholder routes exist for future implementation
- Database initialization must be done before running the app if database features are implemented
- The `.DS_Store` and `__pycache__/` files are ignored but may appear in version control
- Debug mode is enabled in development for auto-reload; disable in production

## Troubleshooting

- **Database file (instance.db) is created at runtime** and is in `.gitignore` — it won't be tracked in version control
- **Routes return placeholder strings** if they show "coming in Step X", the corresponding database/feature functions haven't been implemented yet
- **Port 5001 is in use?** Change the port in the `if __name__ == "__main__"` block in `app.py`
