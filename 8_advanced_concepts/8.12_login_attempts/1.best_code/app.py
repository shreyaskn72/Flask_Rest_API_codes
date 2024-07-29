from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    locked = db.Column(db.Boolean, default=False)
    login_attempts = db.relationship('LoginAttempt', backref='user', lazy=True)

# Login attempt model
class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attempts = db.Column(db.Integer, default=0)
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

def login_attempts_tracker(login_attempt, user):
    # Track login attempts and lockout account if more than 5 attempts
    if login_attempt:
        login_attempt.attempts += 1
        if login_attempt.attempts >= 5:
            login_attempt.lockout_time = get_lockout_time()
            if datetime.now() > login_attempt.lockout_time + timedelta(minutes=30):
                user.locked = True
    else:
        new_login_attempt = LoginAttempt(user_id=user.id, attempts=1)
        db.session.add(new_login_attempt)
    db.session.commit()



# API endpoint for user login
# API endpoint for user login
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    # Check if email exists and user is not locked
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found'}), 404

    if user.locked:
        return jsonify({'error': 'Account permanently locked. Please contact support.'}), 403

    # Check if account is locked out
    login_attempt = LoginAttempt.query.filter_by(user_id=user.id).first()
    if login_attempt and login_attempt.lockout_time and datetime.now() < login_attempt.lockout_time:
        return jsonify({'error': 'Account locked out for 30 minutes. Please try again later.'}), 403

    # Check password
    if check_password_hash(user.password_hash, password):
        # Reset login attempts if successful login
        if login_attempt:
            db.session.delete(login_attempt)
            db.session.commit()
        return jsonify({'message': 'Login successful'}), 200
    else:
        login_attempts_tracker(login_attempt, user)
        return jsonify({'error': 'Incorrect password'}), 401


# API endpoint to fetch user by user id
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_data = {
        'id': user.id,
        'email': user.email,
        'locked': user.locked
    }

    # Get login attempts related to the user
    login_attempts = LoginAttempt.query.filter_by(user_id=user.id).all()
    login_attempts_data = []
    for attempt in login_attempts:
        attempt_data = {
            'id': attempt.id,
            'attempts': attempt.attempts,
            'lockout_time': attempt.lockout_time.strftime("%Y-%m-%d %H:%M:%S") if attempt.lockout_time else None
        }
        login_attempts_data.append(attempt_data)

    user_data['login_attempts'] = login_attempts_data

    return jsonify(user_data), 200

# API endpoint to unlock a user account and delete login attempts
@app.route('/unlock/<int:user_id>', methods=['PUT'])
def unlock_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Unlock the user account
    user.locked = False

    # Delete login attempts
    login_attempt = LoginAttempt.query.filter_by(user_id=user_id).first()
    if login_attempt:
        db.session.delete(login_attempt)

    db.session.commit()

    return jsonify({'message': 'User account unlocked successfully'}), 200


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
