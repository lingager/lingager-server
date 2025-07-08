# server.py
from flask import Flask, request, jsonify
from database import get_license_status, init_db

app = Flask(__name__)

@app.route('/check_license', methods=['POST'])
def check_license():
    data = request.get_json()
    if not data or 'license_id' not in data:
        return jsonify({'error': 'Missing license_id'}), 400

    license_id = data['license_id']
    status = get_license_status(license_id)

    if status:
        return jsonify({'status': status})
    else:
        return jsonify({'status': 'not_found'}), 404

# Run this once when you first set up the server
@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

if __name__ == '__main__':
    # For local testing only
    app.run(debug=True)