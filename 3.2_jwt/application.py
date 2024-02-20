# Import Flask and other libraries
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Create a Flask app and configure the database and JWT secret key
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your secret key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)

# Create a SQLAlchemy object and a database model
db = SQLAlchemy(app)

class User(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(50), unique=True, nullable=False)
   password = db.Column(db.String(100), nullable=False)
   role = db.Column(db.String(10), nullable=False) # admin or user

   def __repr__(self):
      return f"<User {self.username}>"

   def to_dict(self):
       return {
           "id": self.id,
           "username": self.username,
           "role": self.role
       }

# Create a JWTManager object and a custom claim for user role
jwt = JWTManager(app)



@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    user = User.query.filter_by(username=identity).first()
    return {
               "role": user.role
            }

# Define a route for user registration
@app.route("/register", methods=["POST"])
def register():
   data = request.get_json()
   username = data.get("username")
   password = data.get("password")
   role = data.get("role")

   # Validate the input data
   if not username or not password or not role:
         return jsonify({"message": "Missing data"}), 400
   if User.query.filter_by(username=username).first():
         return jsonify({"message": "Username already exists"}), 409
   if role not in ["admin", "user"]:
          return jsonify({"message": "Invalid role"}), 400

   # Hash the password and create a new user
   password_hash = generate_password_hash(password)
   new_user = User(username=username, password=password_hash, role=role)
   db.session.add(new_user)
   db.session.commit()

   print("new_user is")
   print(new_user)
   print(new_user.to_dict())
   new_user_dict = new_user.to_dict()

   # Return a success message
   return jsonify({"registered_user":new_user_dict, "message": "User registered successfully"}), 201

# Define a route for user login
@app.route("/login", methods=["POST"])
def login():
  data = request.get_json()
  username = data.get("username")
  password = data.get("password")

  # Validate the input data
  if not username or not password:
     return jsonify({"message": "Missing data"}), 400

  # Check the user credentials
  user = User.query.filter_by(username=username).first()
  if not user or not check_password_hash(user.password, password):
       return jsonify({"message": "Invalid credentials"}), 401

  # Generate an access token
  access_token = create_access_token(identity=username)

  # Return the access token
  return jsonify({"access_token": access_token}), 200

# Define a route for getting all users (only for admin role)
@app.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    # Check the user role from the JWT claims
    claims = get_jwt()
    print("claims is")
    print(claims)
    if claims["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    # Query all users from the database
    users = User.query.all()

    # Convert the users to a list of dictionaries
    users = [user.to_dict() for user in users]

    # Convert the users to a list of dictionaries
    #users = [{"id": user.id, "username": user.username, "role": user.role} for user in users]

   # Return the users as JSON
    return jsonify({"users": users}), 200

# Define a route for getting the current user
@app.route("/me", methods=["GET"], endpoint='get_me')
@jwt_required()
def get_me():
   # Get the current user from the JWT identity
   username = get_jwt_identity()
   user = User.query.filter_by(username=username).first()

   print("username is", username)
   print("user is", user)

   print(user.to_dict())

   # Convert the user to a dictionary
   user = {"id": user.id, "username": user.username, "role": user.role}

   # Return the user as JSON
   return jsonify({"user": user}), 200

# Run the app

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)

"""

This program creates a SQLite database with a table named User, and defines four routes for user registration, login, getting all users, and getting the current user. It uses the Flask-JWT-Extended library to handle the creation and verification of JWT tokens, and to add a custom claim for the user role. It also uses the werkzeug.security library to hash and check the user passwords. It uses decorators to protect the routes that require authentication and authorization.

You can test the program by running it and sending requests to the different routes with the appropriate data and headers. For example, you can use curl to send requests like this:

# Register a new user with the admin role
curl -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123", "role": "admin"}' http://localhost:5000/register

# Register a new user with the user role
curl -X POST -H "Content-Type: application/json" -d '{"username": "user", "password": "user123", "role": "user"}' http://localhost:5000/register

# Login as the admin user and get the access token
curl -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123"}' http://localhost:5000/login

# Login as the user and get the access token
curl -X POST -H "Content-Type: application/json" -d '{"username": "user", "password": "user123"}' http://localhost:5000/login

# Get all users as the admin user (use the access token from the previous step)
curl -X GET -H "Authorization: Bearer <access_token>" http://localhost:5000/users

# Get all users as the user (use the access token from the previous step)
curl -X GET -H "Authorization: Bearer <access_token>" http://localhost:5000/users

# Get the current user as the admin user (use the access token from the previous step)
curl -X GET -H "Authorization: Bearer <access_token>" http://localhost:5000/me

# Get the current user as the user (use the access token from the previous step)
curl -X GET -H "Authorization: Bearer <access_token>" http://localhost:5000/me

"""