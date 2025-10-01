# from mcp.server.fastmcp import FastMCP
# import os
# import sqlite3

# CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

# # Create FastMCP server instance
# mcp = FastMCP("ExpenseTracker", host="0.0.0.0", port=8000, auth=None)

# # Use a global connection to keep the in-memory database alive during server runtime
# global_conn = sqlite3.connect(":memory:", check_same_thread=False)


# def init_db():
#     cur = global_conn.cursor()
#     cur.execute(
#         """
#         CREATE TABLE IF NOT EXISTS expenses(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             amount REAL NOT NULL,
#             category TEXT NOT NULL,
#             subcategory TEXT DEFAULT '',
#             note TEXT DEFAULT ''
#         )
#         """
#     )
#     global_conn.commit()


# init_db()


# def get_db_connection():
#     # Return the shared global connection for all queries
#     return global_conn


# @mcp.tool()
# def add_expense(date, amount, category, subcategory="", note=""):
#     conn = get_db_connection()
#     cur = conn.execute(
#         "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
#         (date, amount, category, subcategory, note),
#     )
#     conn.commit()
#     return {"status": "ok", "id": cur.lastrowid}


# @mcp.tool()
# def list_expenses(start_date, end_date):
#     conn = get_db_connection()
#     cur = conn.execute(
#         """
#         SELECT id, date, amount, category, subcategory, note
#         FROM expenses
#         WHERE date BETWEEN ? AND ?
#         ORDER BY id ASC
#         """,
#         (start_date, end_date),
#     )
#     cols = [d[0] for d in cur.description]
#     return [dict(zip(cols, row)) for row in cur.fetchall()]


# @mcp.tool()
# def summarize(start_date, end_date, category=None):
#     conn = get_db_connection()
#     query = """
#         SELECT category, SUM(amount) AS total_amount
#         FROM expenses
#         WHERE date BETWEEN ? AND ?
#     """
#     params = [start_date, end_date]

#     if category:
#         query += " AND category = ?"
#         params.append(category)

#     query += " GROUP BY category ORDER BY category ASC"

#     cur = conn.execute(query, params)
#     cols = [d[0] for d in cur.description]
#     return [dict(zip(cols, row)) for row in cur.fetchall()]


# @mcp.tool()
# def edit_expense(
#     expense_id, date=None, amount=None, category=None, subcategory=None, note=None
# ):
#     if not any([date, amount, category, subcategory, note]):
#         return {"status": "error", "message": "No fields to update provided."}
#     set_clauses = []
#     params = []
#     if date is not None:
#         set_clauses.append("date = ?")
#         params.append(date)
#     if amount is not None:
#         set_clauses.append("amount = ?")
#         params.append(amount)
#     if category is not None:
#         set_clauses.append("category = ?")
#         params.append(category)
#     if subcategory is not None:
#         set_clauses.append("subcategory = ?")
#         params.append(subcategory)
#     if note is not None:
#         set_clauses.append("note = ?")
#         params.append(note)

#     params.append(expense_id)
#     query = f"UPDATE expenses SET {', '.join(set_clauses)} WHERE id = ?"
#     conn = get_db_connection()
#     conn.execute(query, params)
#     conn.commit()
#     return {"status": "ok"}


# @mcp.tool()
# def delete_expense(expense_id):
#     conn = get_db_connection()
#     conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
#     conn.commit()
#     return {"status": "ok"}


# @mcp.resource("expense://categories", mime_type="application/json")
# def categories():
#     with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
#         return f.read()


# # No explicit mcp.run() call needed; MCP framework manages server startup and asyncio loop

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SimpleTest", host="0.0.0.0", port=8000)


@mcp.tool()
def ping():
    return "pong"


# No explicit mcp.run()
