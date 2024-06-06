from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users2.db'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    login_attempts = db.Column(db.Integer, default=0)
    lockout_time = db.Column(db.DateTime)

# Create tables
db.create_all()

# Function to calculate lockout time
def get_lockout_time():
    return datetime.now() + timedelta(minutes=30)

# API endpoint for user registration
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Hash the password before saving
    hashed_password = generate_password_hash(password)

    # Save user data
    new_user = User(email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# API endpoint for user login
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    # Check if email exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found'}), 404

    # Check if account is locked out
    if user.lockout_time and datetime.now() < user.lockout_time:
        return jsonify({'error': 'Account locked out. Please try again later.'}), 403

    # Check password
    if check_password_hash(user.password_hash, password):
        # Reset login attempts if successful login
        user.login_attempts = 0
        user.lockout_time = None
        db.session.commit()
        return jsonify({'message': 'Login successful'}), 200
    else:
        # Track login attempts and lockout account if more than 5 attempts
        user.login_attempts += 1
        if user.login_attempts >= 5:
            user.lockout_time = get_lockout_time()
        db.session.commit()
        return jsonify({'error': 'Incorrect password'}), 401

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
