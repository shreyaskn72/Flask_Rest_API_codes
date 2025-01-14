from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'  # Change this to your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')

    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.profile = Profile()

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

# Routes
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'username': user.username, 'email': user.email} for user in users])

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'username': user.username, 'email': user.email, 'profile': {'full_name': user.profile.full_name if user.profile else None}})

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    # Check if username or email already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({'error': 'Username or email already exists'}), 400

    # Create User with Profile
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/users/<int:user_id>/profile', methods=['PUT'])
def update_profile(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.profile.full_name = data.get('full_name', user.profile.full_name if user.profile else None)
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})

@app.route('/users/<int:user_id>/fullname', methods=['PUT'])
def update_fullname(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_full_name = data.get('full_name')

    # Check if full name already exists for another user
    existing_profile = Profile.query.filter(Profile.full_name == new_full_name).first()
    if existing_profile and existing_profile.user_id != user.id:
        return jsonify({'error': 'Full name already exists for another user'}), 400

    user.profile.full_name = new_full_name
    db.session.commit()
    return jsonify({'message': 'Full name updated successfully'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
