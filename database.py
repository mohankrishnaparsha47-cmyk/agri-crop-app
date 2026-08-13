import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "farmer_assistant.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            state TEXT,
            district TEXT,
            land_holding_acres REAL,
            category TEXT,          -- General / SC / ST / OBC
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS field_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            crop_name TEXT NOT NULL,
            activity TEXT NOT NULL,      -- Sowing, Fertilizer applied, Irrigation, Harvest, etc.
            notes TEXT,
            activity_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS scheme_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            scheme_name TEXT NOT NULL,
            status TEXT DEFAULT 'Applied',   -- Applied, Under Review, Approved, Rejected
            applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def create_default_admin():
    """Creates a default admin account if it doesn't already exist."""
    from werkzeug.security import generate_password_hash
    conn = get_connection()
    existing = conn.execute("SELECT id FROM users WHERE phone = ?", ("9999900000",)).fetchone()
    if not existing:
        conn.execute(
            """INSERT INTO users (name, phone, password_hash, state, district,
               land_holding_acres, category, is_admin)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ("Admin", "9999900000", generate_password_hash("admin123"),
             "Telangana", "HQ", 0, "General", 1)
        )
        conn.commit()
        print("Default admin created -> phone: 9999900000 | password: admin123")
    conn.close()


if __name__ == "__main__":
    init_db()
    create_default_admin()
