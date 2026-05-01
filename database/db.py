import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE = os.path.join(os.path.dirname(__file__), '..', 'instance', 'expense_tracker.db')

VALID_CATEGORIES = ['Food', 'Transport', 'Bills', 'Health', 'Entertainment', 'Shopping', 'Others']


def get_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn


def init_db():
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount DECIMAL(10,2) NOT NULL CHECK(amount > 0),
                category TEXT NOT NULL DEFAULT 'Others',
                date DATE NOT NULL,
                description TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
            CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
        """)
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"Database initialization failed: {e}")
    finally:
        conn.close()


def seed_db():
    conn = get_db()
    try:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM expenses")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('users', 'expenses')")

        users = [
            ("John Doe", "john@example.com", generate_password_hash("password123")),
            ("Jane Smith", "jane@example.com", generate_password_hash("password456")),
        ]
        cursor.executemany(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)", users
        )

        expenses = [
            (1, 500.00, 'Food',          '2026-04-20', 'Weekly groceries'),
            (1, 150.00, 'Transport',     '2026-04-22', 'Uber ride to office'),
            (1, 2000.00,'Bills',         '2026-04-01', 'Electricity bill'),
            (1, 800.00, 'Health',        '2026-04-15', 'Doctor visit'),
            (1, 300.00, 'Entertainment', '2026-04-25', 'Movie tickets'),
            (1, 1200.00,'Shopping',      '2026-04-18', 'New t-shirts'),
            (1, 100.00, 'Others',        '2026-04-26', 'Miscellaneous'),
            (2, 600.00, 'Food',          '2026-04-21', 'Lunch meeting'),
            (2, 200.00, 'Transport',     '2026-04-23', 'Cab ride'),
            (2, 1500.00,'Bills',         '2026-04-05', 'Internet bill'),
            (2, 400.00, 'Health',        '2026-04-10', 'Pharmacy'),
            (2, 500.00, 'Entertainment', '2026-04-24', 'Concert tickets'),
            (2, 2500.00,'Shopping',      '2026-04-19', 'Formal dress'),
            (2, 50.00,  'Others',        '2026-04-27', 'Parking'),
        ]
        cursor.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"Seeding failed: {e}")
    finally:
        conn.close()
