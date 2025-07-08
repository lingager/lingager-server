# database.py
import sqlite3

DATABASE_FILE = 'licenses.db'

def get_db_connection():
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def init_db():
    """Creates the database table if it doesn't exist."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_id TEXT NOT NULL UNIQUE,
                customer_email TEXT,
                status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'expired', 'cancelled')),
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("Database initialized.")

def get_license_status(license_id):
    """Fetches the status of a given license key."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT status FROM licenses WHERE license_id = ?", (license_id,))
        result = cursor.fetchone()
        return result['status'] if result else None

def add_new_license(license_id, email):
    """Adds a new license to the database."""
    with get_db_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO licenses (license_id, customer_email) VALUES (?, ?)",
                (license_id, email)
            )
            conn.commit()
            return True, "License added successfully."
        except sqlite3.IntegrityError:
            return False, "This license ID already exists."

def update_license_status(license_id, new_status):
    """Updates the status of an existing license."""
    if new_status not in ['active', 'expired', 'cancelled']:
        return False, "Invalid status."
        
    with get_db_connection() as conn:
        cursor = conn.execute(
            "UPDATE licenses SET status = ? WHERE license_id = ?",
            (new_status, license_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return False, "License ID not found."
        return True, f"License status updated to {new_status}."

def get_all_licenses():
    """Retrieves all licenses for admin viewing."""
    with get_db_connection() as conn:
        licenses = conn.execute("SELECT id, license_id, customer_email, status, creation_date FROM licenses").fetchall()
        return [dict(license) for license in licenses]
