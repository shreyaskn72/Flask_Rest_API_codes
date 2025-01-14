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
    profile = db.relationship('Profile', backref='user', uselist=False)

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
    return jsonify({'username': user.username, 'email': user.email, 'profile': {'full_name': user.profile.full_name}})

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    full_name = data.get('full_name')

    # Create User and Profile
    user = User(username=username, email=email)
    profile = Profile(full_name=full_name)
    user.profile = profile

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.profile.full_name = data.get('full_name', user.profile.full_name)
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

#endpoint to update only profile
@app.route('/users/<int:user_id>/profile', methods=['PUT'])
def update_profile(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.profile.full_name = data.get('full_name', user.profile.full_name)
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
