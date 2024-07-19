Give one flask api example for Crud operation. Use sqlite/mysql database. Use redis too

Certainly! Let's create a Flask API example that performs CRUD (Create, Read, Update, Delete) operations using SQLite as the main database and Redis for caching. SQLite will be used for storing persistent data, while Redis will be used for caching retrieved data to improve performance.

### Prerequisites:

1. Install required Python packages:
   - Flask: Web framework for creating APIs.
   - Flask-RESTful: Extension for building REST APIs with Flask.
   - Flask-SQLAlchemy: SQLAlchemy integration with Flask for database operations.
   - Flask-Redis: Redis integration with Flask for caching.

   You can install these packages using pip:

   ```bash
   pip install Flask Flask-RESTful Flask-SQLAlchemy Flask-Redis
   ```

2. Ensure you have Redis installed and running locally (`redis-server`).

### Example Flask API with SQLite and Redis

#### `app.py` - Main Flask Application

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crud_example.db'  # SQLite database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['REDIS_URL'] = "redis://localhost:6379/0"  # Redis URL
db = SQLAlchemy(app)
redis_client = FlaskRedis(app)

# Example Model: User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Routes for CRUD operations

# Create operation - POST request to create a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message='User created successfully'), 201

# Read operation - GET request to retrieve all users
@app.route('/users', methods=['GET'])
def get_all_users():
    # Try to fetch users from Redis cache
    cached_users = redis_client.get('users')
    if cached_users:
        users = cached_users.decode('utf-8')
        return jsonify(users=eval(users))

    # If not in cache, fetch from SQLite database
    users = User.query.all()
    users_data = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]

    # Store fetched users in Redis cache with a TTL (e.g., 1 hour)
    redis_client.set('users', str(users_data), ex=3600)

    return jsonify(users=users_data)

# Update operation - PUT request to update an existing user by ID
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify(message='User not found'), 404

    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()

    # Clear cached users data in Redis after update
    redis_client.delete('users')

    return jsonify(message='User updated successfully')

# Delete operation - DELETE request to delete a user by ID
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify(message='User not found'), 404

    db.session.delete(user)
    db.session.commit()

    # Clear cached users data in Redis after delete
    redis_client.delete('users')

    return jsonify(message='User deleted successfully')

if __name__ == '__main__':
    # Create SQLite database tables based on defined models
    db.create_all()
    app.run(debug=True)
```

### Explanation:

- **Flask Configuration**: Configures Flask to use SQLite as the database (`crud_example.db`) and sets up SQLAlchemy (`db`) for ORM operations.
- **Model**: Defines a simple `User` model with `id`, `username`, and `email` fields.
- **Routes and CRUD Operations**:
  - **Create (`POST /users`)**: Creates a new user in the SQLite database.
  - **Read (`GET /users`)**: Retrieves all users. Uses Redis for caching to improve performance.
  - **Update (`PUT /users/<user_id>`)**: Updates an existing user by ID in the SQLite database.
  - **Delete (`DELETE /users/<user_id>`)**: Deletes a user by ID from the SQLite database.
- **Redis Integration**:
  - Utilizes `FlaskRedis` extension to connect to Redis (`redis_client`).
  - Caches retrieved users data (`GET /users`) in Redis to avoid querying the database repeatedly, improving API response times.
  - Clears cached data (`DELETE /users/<user_id>`, `PUT /users/<user_id>`) in Redis after performing update or delete operations to ensure data consistency.

### Testing the API:

- Start the Flask development server by running `python app.py`.
- Use tools like `curl`, Postman, or your browser to test CRUD operations (`POST /users`, `GET /users`, `PUT /users/<user_id>`, `DELETE /users/<user_id>`).

This example demonstrates how to build a Flask API with CRUD operations using SQLite for persistent storage and Redis for caching, enhancing performance and scalability of your application. Adjust the example as needed based on your specific requirements and deployment environment.
