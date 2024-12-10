from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Import CORS

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

# Create the database tables (if they don't exist)
with app.app_context():
    db.create_all()

# Enable CORS for specific domains
allowed_origins = [
    'http://localhost:3000',  # Example: Allow requests from your local frontend
    'https://your-frontend-domain.com',  # Example: Allow requests from your production frontend
]

CORS(app, origins=allowed_origins, methods=["GET", "POST", "PUT", "DELETE"])  # Restrict CORS

# Create a user
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"message": "Name and email are required!"}), 400

    user = User(name=name, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully!", "id": user.id}), 201

# Read all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "name": user.name, "email": user.email} for user in users]), 200

# Read a single user
@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify({"id": user.id, "name": user.name, "email": user.email}), 200
    return jsonify({"message": "User not found!"}), 404

# Update a user
@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "User not found!"}), 404

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if name:
        user.name = name
    if email:
        user.email = email

    db.session.commit()

    return jsonify({"message": "User updated successfully!"}), 200

# Delete a user
@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "User not found!"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully!"}), 200

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
