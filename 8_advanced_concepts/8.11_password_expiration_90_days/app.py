from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Dummy database to store user data
users = {}

# Function to calculate the password expiration date
def get_password_expiration_date():
    return datetime.now() + timedelta(days=90)

# API endpoint for user registration
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    # Check if username already exists
    if username in users:
        return jsonify({'error': 'Username already exists'}), 400

    # Save user data
    users[username] = {
        'password': password,
        'password_created_at': datetime.now(),
        'password_expires_at': get_password_expiration_date()
    }

    return jsonify({'message': 'User registered successfully'}), 201

# API endpoint for password change
@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.get_json()

    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    # Check if username exists
    if username not in users:
        return jsonify({'error': 'User not found'}), 404

    # Check if old password matches
    if users[username]['password'] != old_password:
        return jsonify({'error': 'Invalid old password'}), 400

    # Update password and expiration date
    users[username]['password'] = new_password
    users[username]['password_created_at'] = datetime.now()
    users[username]['password_expires_at'] = get_password_expiration_date()

    return jsonify({'message': 'Password changed successfully'}), 200

# API endpoint to validate if password has expired
@app.route('/password_expired', methods=['POST'])
def password_expired():
    data = request.get_json()

    username = data.get('username')

    # Check if username exists
    if username not in users:
        return jsonify({'error': 'User not found'}), 404

    # Check if password has expired
    password_expires_at = users[username]['password_expires_at']
    if datetime.now() > password_expires_at:
        return jsonify({'message': 'Password has expired'}), 200
    else:
        return jsonify({'message': 'Password is still valid'}), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
