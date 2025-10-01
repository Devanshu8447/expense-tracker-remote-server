from mcp.server.fastmcp import FastMCP
import os
import sqlite3

# Remove or comment out DB_PATH as it will be in-memory
# DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

# Keep host and port as they were; FastMCP Cloud handles mapping to 8080 internally
mcp = FastMCP(
    "ExpenseTracker", host="0.0.0.0", port=8000
)  # Or keep auth=None if you've done that


def init_db():
    # Connect to an in-memory database for cloud deployment
    with sqlite3.connect(":memory:") as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """
        )


init_db()  # Call init_db immediately as before


# IMPORTANT: Update all functions to use ":memory:" or pass a connection object
# A cleaner way is to create a function to get the connection
def get_db_connection():
    # For simplicity, connect to in-memory directly in each function for now
    # In a real app, you'd use a connection pool or a global connection for in-memory
    return sqlite3.connect(":memory:")


@mcp.tool()
def add_expense(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to the database."""
    with get_db_connection() as c:  # Use the helper function
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note),
        )
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool()
def list_expenses(start_date, end_date):
    """List expense entries within an inclusive date range."""
    with get_db_connection() as c:  # Use the helper function
        cur = c.execute(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (start_date, end_date),
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool()
def summarize(start_date, end_date, category=None):
    """Summarize expenses by category within an inclusive date range."""
    with get_db_connection() as c:  # Use the helper function
        query = """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
            """
        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"

        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool()
def edit_expense(
    expense_id, date=None, amount=None, category=None, subcategory=None, note=None
):
    """Edit an existing expense or credit entry by ID."""
    if not any([date, amount, category, subcategory, note]):
        return {"status": "error", "message": "No fields to update provided."}
    set_clauses = []
    params = []
    if date is not None:
        set_clauses.append("date = ?")
        params.append(date)
    if amount is not None:
        set_clauses.append("amount = ?")
        params.append(amount)
    if category is not None:
        set_clauses.append("category = ?")
        params.append(category)
    if subcategory is not None:
        set_clauses.append("subcategory = ?")
        params.append(subcategory)
    if note is not None:
        set_clauses.append("note = ?")
        params.append(note)

    params.append(expense_id)

    query = f"UPDATE expenses SET {', '.join(set_clauses)} WHERE id = ?"
    with get_db_connection() as c:  # Use the helper function
        c.execute(query, params)
    return {"status": "ok"}


@mcp.tool()
def delete_expense(expense_id):
    """Delete an expense or credit entry by ID."""
    with get_db_connection() as c:  # Use the helper function
        c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    return {"status": "ok"}


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    # This assumes categories.json is present in the deployed package
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()


# Start the server
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http"
    )  # Use streamable-http for cloud deployment generally
