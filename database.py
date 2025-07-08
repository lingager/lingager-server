# database.py (PostgreSQL Version)
import os
import psycopg2
from psycopg2.extras import DictCursor

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    # This will get the DATABASE_URL from Render's environment variables
    conn_string = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(conn_string)
    return conn

def init_db():
    """Creates the database table if it doesn't exist."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS licenses (
                    id SERIAL PRIMARY KEY,
                    license_id TEXT NOT NULL UNIQUE,
                    customer_email TEXT,
                    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'expired', 'cancelled')),
                    creation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        conn.commit()
    print("Database initialized.")

def get_license_status(license_id):
    """Fetches the status of a given license key."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT status FROM licenses WHERE license_id = %s", (license_id,))
            result = cur.fetchone()
            return result['status'] if result else None

def add_new_license(license_id, email):
    """Adds a new license to the database."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO licenses (license_id, customer_email) VALUES (%s, %s)",
                    (license_id, email)
                )
                conn.commit()
                return True, "License added successfully."
            except psycopg2.IntegrityError:
                # This error occurs if the license_id already exists (UNIQUE constraint)
                conn.rollback()
                return False, "This license ID already exists."

def update_license_status(license_id, new_status):
    """Updates the status of an existing license."""
    if new_status not in ['active', 'expired', 'cancelled']:
        return False, "Invalid status."
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE licenses SET status = %s WHERE license_id = %s",
                (new_status, license_id)
            )
            conn.commit()
            if cur.rowcount == 0:
                return False, "License ID not found."
            return True, f"License status updated to {new_status}."

def get_all_licenses():
    """Retrieves all licenses for admin viewing."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT id, license_id, customer_email, status, creation_date FROM licenses")
            licenses = cur.fetchall()
            # Convert list of DictRow objects to list of dictionaries
            return [dict(row) for row in licenses]
