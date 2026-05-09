import os
import sqlite3
from datetime import date
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, init_db, seed_db, VALID_CATEGORIES

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize DB on startup
with app.app_context():
    init_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template("register.html")

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password))
            )
            db.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered.", "error")
            return render_template("register.html")
        finally:
            db.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        try:
            user = db.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
        finally:
            db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("profile"))

        flash("Invalid email or password.", "error")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Authenticated Routes                                                #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/analytics")
def analytics():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("analytics.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    try:
        user = db.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

        if not user:
            session.clear()
            return redirect(url_for("login"))

        stats = db.execute(
            """SELECT COUNT(*) AS expense_count,
                      COALESCE(SUM(amount), 0) AS total_spent,
                      COALESCE(AVG(amount), 0) AS avg_expense
               FROM expenses WHERE user_id = ?""",
            (session["user_id"],)
        ).fetchone()

        expense_list = db.execute(
            """SELECT id, date, category, amount, description
               FROM expenses WHERE user_id = ?
               ORDER BY date ASC""",
            (session["user_id"],)
        ).fetchall()
    finally:
        db.close()

    if request.method == "POST":
        new_name = request.form.get("name", "").strip()
        new_password = request.form.get("new_password", "")
        confirm_pw = request.form.get("confirm_password", "")

        errors = []
        if not new_name:
            errors.append("Name cannot be empty.")

        changing_password = bool(new_password or confirm_pw)
        if changing_password:
            if len(new_password) < 8:
                errors.append("New password must be at least 8 characters.")
            if new_password != confirm_pw:
                errors.append("Passwords do not match.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("profile.html", user=user,
                                   stats=stats, expense_list=expense_list)

        db = get_db()
        try:
            if changing_password:
                db.execute(
                    "UPDATE users SET name = ?, password = ? WHERE id = ?",
                    (new_name, generate_password_hash(new_password), session["user_id"])
                )
            else:
                db.execute(
                    "UPDATE users SET name = ? WHERE id = ?",
                    (new_name, session["user_id"])
                )
            db.commit()
            session["user_name"] = new_name
            flash("Profile updated.", "success")
        except sqlite3.Error:
            db.rollback()
            flash("Failed to update profile.", "error")
        finally:
            db.close()

        return redirect(url_for("profile"))

    return render_template("profile.html", user=user,
                           stats=stats, expense_list=expense_list)


@app.route("/expenses")
def expenses():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    try:
        user_expenses = db.execute(
            "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC",
            (session["user_id"],)
        ).fetchall()
    finally:
        db.close()

    return render_template("expenses.html", expenses=user_expenses, categories=VALID_CATEGORIES)


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        amount = request.form.get("amount")
        category = request.form.get("category", "Others")
        expense_date = request.form.get("date")
        description = request.form.get("description", "").strip()

        errors = []
        try:
            amount = float(amount)
            if amount <= 0:
                errors.append("Amount must be greater than zero.")
        except (TypeError, ValueError):
            errors.append("Invalid amount.")

        if category not in VALID_CATEGORIES:
            errors.append("Invalid category.")

        if not expense_date:
            errors.append("Date is required.")
        elif expense_date > str(date.today()):
            errors.append("Expense date cannot be in the future.")

        if description and len(description) > 500:
            errors.append("Description must be 500 characters or fewer.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("add_expense.html", categories=VALID_CATEGORIES)

        db = get_db()
        try:
            db.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (session["user_id"], amount, category, expense_date, description or None)
            )
            db.commit()
            flash("Expense added.", "success")
            return redirect(url_for("expenses"))
        except sqlite3.Error as e:
            db.rollback()
            flash("Failed to save expense.", "error")
            return render_template("add_expense.html", categories=VALID_CATEGORIES)
        finally:
            db.close()

    return render_template("add_expense.html", categories=VALID_CATEGORIES)


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    try:
        expense = db.execute(
            "SELECT * FROM expenses WHERE id = ? AND user_id = ?",
            (id, session["user_id"])
        ).fetchone()

        if not expense:
            flash("Expense not found.", "error")
            return redirect(url_for("expenses"))

        if request.method == "POST":
            amount = request.form.get("amount")
            category = request.form.get("category", "Others")
            expense_date = request.form.get("date")
            description = request.form.get("description", "").strip()

            errors = []
            try:
                amount = float(amount)
                if amount <= 0:
                    errors.append("Amount must be greater than zero.")
            except (TypeError, ValueError):
                errors.append("Invalid amount.")

            if category not in VALID_CATEGORIES:
                errors.append("Invalid category.")
            if not expense_date:
                errors.append("Date is required.")
            elif expense_date > str(date.today()):
                errors.append("Expense date cannot be in the future.")
            if description and len(description) > 500:
                errors.append("Description must be 500 characters or fewer.")

            if errors:
                for error in errors:
                    flash(error, "error")
                return render_template("edit_expense.html", expense=expense, categories=VALID_CATEGORIES)

            db.execute(
                "UPDATE expenses SET amount=?, category=?, date=?, description=? WHERE id=? AND user_id=?",
                (amount, category, expense_date, description or None, id, session["user_id"])
            )
            db.commit()
            flash("Expense updated.", "success")
            return redirect(url_for("expenses"))

    except sqlite3.Error as e:
        db.rollback()
        flash("Failed to update expense.", "error")
    finally:
        db.close()

    return render_template("edit_expense.html", expense=expense, categories=VALID_CATEGORIES)


@app.route("/expenses/<int:id>/delete", methods=["POST"])
def delete_expense(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    try:
        db.execute(
            "DELETE FROM expenses WHERE id = ? AND user_id = ?",
            (id, session["user_id"])
        )
        db.commit()
        flash("Expense deleted.", "success")
    except sqlite3.Error:
        db.rollback()
        flash("Failed to delete expense.", "error")
    finally:
        db.close()

    return redirect(url_for("expenses"))


# ------------------------------------------------------------------ #
# Admin Routes (Development Only)                                     #
# ------------------------------------------------------------------ #

@app.route("/admin/seed", methods=["POST"])
def seed_database():
    if not app.debug:
        return jsonify({"error": "Not available in production"}), 403
    try:
        seed_db()
        return jsonify({"success": True, "message": "Database seeded successfully"})
    except RuntimeError as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ------------------------------------------------------------------ #
# Error Handlers                                                      #
# ------------------------------------------------------------------ #

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
