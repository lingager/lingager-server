# server.py
import os
from flask import Flask, request, jsonify
from database import (
    get_license_status, 
    init_db, 
    add_new_license, 
    update_license_status,
    get_all_licenses
)

app = Flask(__name__)

# --- Configuration ---
# This uses the secret key you set as an environment variable on Render.
ADMIN_API_KEY = os.environ.get('LINGAGER_ADMIN_KEY', 'default_secret_key_for_testing')

# --- Public Endpoints ---

@app.route('/check_license', methods=['POST'])
def check_license():
    """
    Endpoint for the compiled EXE to check its license status.
    """
    data = request.get_json()
    if not data or 'license_id' not in data:
        return jsonify({'error': 'Missing license_id'}), 400

    license_id = data['license_id']
    status = get_license_status(license_id)

    if status:
        return jsonify({'status': status})
    else:
        # This is correct, it tells your app the license isn't on the server yet.
        return jsonify({'status': 'not_found'}), 404

@app.route('/health', methods=['GET'])
def health_check():
    """
    A simple endpoint for an uptime monitor to hit to keep the server awake.
    """
    return jsonify({'status': 'ok'}), 200


# =====================================================================
# --- Admin Endpoints (for you to manage customers) ---
# =====================================================================

def is_admin():
    """Helper function to check for the admin API key."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or 'Bearer' not in auth_header:
        return False
    # The token is "Bearer <key>"
    try:
        token = auth_header.split(" ")[1]
        return token == ADMIN_API_KEY
    except IndexError:
        return False

@app.route('/admin/licenses', methods=['GET'])
def admin_get_licenses():
    """View all licenses."""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    all_licenses = get_all_licenses()
    return jsonify(all_licenses)

@app.route('/admin/licenses', methods=['POST'])
def admin_add_license():
    """Add a new license."""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    license_id = data.get('license_id')
    email = data.get('customer_email')
    if not license_id or not email:
        return jsonify({'error': 'Missing license_id or customer_email'}), 400

    success, message = add_new_license(license_id, email)
    if success:
        return jsonify({'message': message}), 201
    else:
        return jsonify({'error': message}), 409 # 409 Conflict: already exists

@app.route('/admin/licenses/<string:license_id>', methods=['PATCH'])
def admin_update_license(license_id):
    """Update a license status (e.g., to 'expired' or 'cancelled')."""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    new_status = data.get('status')
    if not new_status:
        return jsonify({'error': 'Missing new status'}), 400

    success, message = update_license_status(license_id, new_status)
    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 404 # 404 Not Found


# --- CLI Command ---
@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()

if __name__ == '__main__':
    # For local testing only
    app.run(debug=True)
