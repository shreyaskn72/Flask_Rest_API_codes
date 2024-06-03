from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def validate_password(password, first_name, last_name, middle_name):
    # Check password length
    if not (9 <= len(password) <= 20):
        return False, 'Password length should be between 9 and 20 characters.'

    # Check for uppercase, lowercase, digit, and special character
    if not re.search(r"[A-Z]", password):
        return False, 'Password should contain at least one uppercase letter.'

    if not re.search(r"[a-z]", password):
        return False, 'Password should contain at least one lowercase letter.'

    if not re.search(r"\d", password):
        return False, 'Password should contain at least one digit.'

    if not re.search(r"[!@#$%^&*()_+{}|:<>?~-]", password):
        return False, 'Password should contain at least one special character.'

    # Check if password contains first name, last name, or middle name
    if (first_name.lower() in password.lower() or
        last_name.lower() in password.lower() or
        (middle_name and middle_name.lower() in password.lower())):
        return False, 'Password should not contain your first name, last name, or middle name.'

    return True, 'Password is valid.'


@app.route('/register', methods=['POST'])
def register_user():
    # Get the JSON data from the request
    data = request.get_json()

    # Check if all required fields are present
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required.'}), 400

    username = data['username']
    password = data['password']
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    middle_name = data.get('middle_name', '')

    # Validate password
    is_valid, message = validate_password(password, first_name, last_name, middle_name)

    if not is_valid:
        return jsonify({'error': message}), 400

    # If all validation passes, register the user
    # Add your code to save the user to the database or perform any other actions here
    return jsonify({'message': f'User {username} registered successfully.'}), 200

if __name__ == '__main__':
    app.run(debug=True)
