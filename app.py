import os
from datetime import date
from decimal import Decimal, InvalidOperation

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, url_for
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-before-deploying")


def get_db_connection():
    """Open a connection to the MySQL database."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "spendsmart"),
    )


def get_dashboard_data():
    """Return this month's income, expenses, and category totals."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN transaction_type = 'income'
                THEN amount ELSE 0 END), 0) AS total_income,
            COALESCE(SUM(CASE WHEN transaction_type = 'expense'
                THEN amount ELSE 0 END), 0) AS total_expenses
        FROM transactions
        WHERE YEAR(transaction_date) = YEAR(CURDATE())
          AND MONTH(transaction_date) = MONTH(CURDATE())
    """)
    totals = cursor.fetchone()

    cursor.execute("""
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE transaction_type = 'expense'
          AND YEAR(transaction_date) = YEAR(CURDATE())
          AND MONTH(transaction_date) = MONTH(CURDATE())
        GROUP BY category
        ORDER BY total DESC
    """)
    category_totals = cursor.fetchall()

    cursor.close()
    connection.close()

    totals["balance"] = totals["total_income"] - totals["total_expenses"]
    return totals, category_totals


@app.route("/")
def index():
    """Show dashboard totals and the most recent transactions."""
    try:
        totals, category_totals = get_dashboard_data()

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM transactions
            ORDER BY transaction_date DESC, id DESC
            LIMIT 8
        """)
        recent_transactions = cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template(
            "index.html",
            totals=totals,
            category_totals=category_totals,
            recent_transactions=recent_transactions,
        )
    except mysql.connector.Error as error:
        app.logger.error("Could not load dashboard: %s", error)
        return render_template("setup_error.html"), 500


@app.route("/transactions")
def transactions():
    """Show all transactions, with optional type and category filters."""
    transaction_type = request.args.get("type", "")
    category = request.args.get("category", "")

    query = "SELECT * FROM transactions WHERE 1=1"
    values = []

    if transaction_type in ("income", "expense"):
        query += " AND transaction_type = %s"
        values.append(transaction_type)

    if category:
        query += " AND category = %s"
        values.append(category)

    query += " ORDER BY transaction_date DESC, id DESC"

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, values)
    all_transactions = cursor.fetchall()

    cursor.execute("SELECT DISTINCT category FROM transactions ORDER BY category")
    categories = [row["category"] for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return render_template(
        "transactions.html",
        transactions=all_transactions,
        categories=categories,
        selected_type=transaction_type,
        selected_category=category,
    )


@app.route("/transactions/add", methods=["GET", "POST"])
def add_transaction():
    """Display the form and save a new transaction."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        transaction_type = request.form.get("transaction_type", "")
        category = request.form.get("category", "").strip()
        amount_text = request.form.get("amount", "").strip()
        transaction_date = request.form.get("transaction_date", "")
        notes = request.form.get("notes", "").strip()

        if not title or not category or not transaction_date or transaction_type not in ("income", "expense"):
            flash("Please fill in all required fields.", "error")
            return render_template("transaction_form.html", transaction=None, today=date.today().isoformat())

        try:
            amount = Decimal(amount_text)
            if amount <= 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            flash("Enter an amount greater than zero.", "error")
            return render_template("transaction_form.html", transaction=None, today=date.today().isoformat())

        try:
            date.fromisoformat(transaction_date)
        except ValueError:
            flash("Please enter a valid date.", "error")
            return render_template("transaction_form.html", transaction=None, today=date.today().isoformat())

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO transactions
                (title, transaction_type, category, amount, transaction_date, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, transaction_type, category, amount, transaction_date, notes))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Transaction added successfully.", "success")
        return redirect(url_for("transactions"))

    return render_template("transaction_form.html", transaction=None, today=date.today().isoformat())


@app.route("/transactions/<int:transaction_id>/edit", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    """Edit an existing transaction."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions WHERE id = %s", (transaction_id,))
    transaction = cursor.fetchone()
    cursor.close()
    connection.close()

    if transaction is None:
        flash("Transaction not found.", "error")
        return redirect(url_for("transactions"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        transaction_type = request.form.get("transaction_type", "")
        category = request.form.get("category", "").strip()
        amount_text = request.form.get("amount", "").strip()
        transaction_date = request.form.get("transaction_date", "")
        notes = request.form.get("notes", "").strip()

        try:
            amount = Decimal(amount_text)
            date.fromisoformat(transaction_date)
            if amount <= 0 or not title or not category or transaction_type not in ("income", "expense"):
                raise ValueError
        except (InvalidOperation, ValueError):
            flash("Please check the form. Amount must be positive and required fields must be filled.", "error")
            return render_template("transaction_form.html", transaction=transaction, today=date.today().isoformat())

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE transactions
            SET title = %s, transaction_type = %s, category = %s,
                amount = %s, transaction_date = %s, notes = %s
            WHERE id = %s
        """, (title, transaction_type, category, amount, transaction_date, notes, transaction_id))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Transaction updated successfully.", "success")
        return redirect(url_for("transactions"))

    return render_template("transaction_form.html", transaction=transaction, today=date.today().isoformat())


@app.route("/transactions/<int:transaction_id>/delete", methods=["POST"])
def delete_transaction(transaction_id):
    """Delete a transaction."""
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = %s", (transaction_id,))
    connection.commit()
    deleted_count = cursor.rowcount
    cursor.close()
    connection.close()

    if deleted_count:
        flash("Transaction deleted.", "success")
    else:
        flash("Transaction not found.", "error")

    return redirect(url_for("transactions"))


if __name__ == "__main__":
    app.run(debug=True)
