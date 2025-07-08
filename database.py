# database.py
import sqlite3

DATABASE_FILE = 'licenses.db'

def init_db():
    """Creates the database table if it doesn't exist."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_id TEXT NOT NULL UNIQUE,
                customer_email TEXT,
                status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'expired', 'cancelled')),
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def get_license_status(license_id):
    """Fetches the status of a given license key."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM licenses WHERE license_id = ?", (license_id,))
        result = cursor.fetchone()
        return result[0] if result else None