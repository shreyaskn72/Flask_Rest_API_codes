Certainly! Here's the full code with a `Flask` app that includes pagination, filtering, searching, sorting, and role-based filtering, along with `curl` commands for testing.

### Full Code (Flask API):

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'  # Use your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User Table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

# Role Table
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# UserRoles Table (many-to-many relationship)
class UserRole(db.Model):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)
    user = db.relationship(User, backref=db.backref('user_roles'))
    role = db.relationship(Role, backref=db.backref('user_roles'))

# API endpoint to get users with pagination, filtering, searching, and sorting
@app.route('/users', methods=['GET'])
def get_users():
    # Get query parameters for pagination, filtering, searching, sorting
    page = request.args.get('page', 1, type=int)  # Default to page 1
    per_page = request.args.get('per_page', 10, type=int)  # Default to 10 items per page
    search = request.args.get('search', '', type=str)  # Search term (username, email)
    sort_by = request.args.get('sort_by', 'id', type=str)  # Sort by 'id' by default
    sort_order = request.args.get('sort_order', 'asc', type=str)  # Sort order, 'asc' or 'desc'
    role_filter = request.args.get('role', '', type=str)  # Comma-separated list of roles

    # Build the query
    query = db.session.query(User).join(UserRole, UserRole.user_id == User.id).join(Role, Role.id == UserRole.role_id)

    # Apply search filter (search users by username or email)
    if search:
        query = query.filter(
            (User.username.like(f'%{search}%')) | 
            (User.email.like(f'%{search}%'))
        )

    # Apply role-based filtering (multiple roles)
    if role_filter:
        roles = role_filter.split(',')  # Split the comma-separated list of roles
        role_filters = [Role.name.like(f'%{role.strip()}%') for role in roles]  # Create a list of 'like' filters for each role
        query = query.filter(or_(*role_filters))  # Apply the 'OR' condition for each role filter

    # Sorting logic
    if sort_by == 'username':
        sort_column = User.username
    elif sort_by == 'email':
        sort_column = User.email
    else:
        sort_column = User.id

    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    users = query.paginate(page, per_page, False)

    # Prepare the result
    result = {
        'total': users.total,
        'pages': users.pages,
        'current_page': users.page,
        'per_page': users.per_page,
        'users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': [{'id': role.id, 'name': role.name} for role in user.roles]
        } for user in users.items]
    }

    return jsonify(result)

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
```

### How to Test with `curl`:

You can now test the API using `curl` commands. Here's how you can use various options:

1. **Start the Flask App**:

   Make sure to install Flask and Flask-SQLAlchemy if you haven't already:

   ```bash
   pip install flask flask_sqlalchemy
   ```

   Then run the Flask application:

   ```bash
   python app.py
   ```

2. **Testing with `curl`**:

   Below are `curl` commands to test various features of the API:

   #### 1. **Get users with pagination (default parameters)**:
   
   ```bash
   curl "http://127.0.0.1:5000/users?page=1&per_page=5"
   ```

   This will return the first 5 users.

   #### 2. **Search users by username or email**:
   
   To search for users whose `username` or `email` contains the string "john":
   
   ```bash
   curl "http://127.0.0.1:5000/users?page=1&per_page=5&search=john"
   ```

   #### 3. **Filter users by multiple roles**:
   
   To filter users who have either "Admin" or "Manager" roles:
   
   ```bash
   curl "http://127.0.0.1:5000/users?page=1&per_page=5&role=Admin,Manager"
   ```

   #### 4. **Combine multiple filters (search + roles + sorting)**:
   
   To search for users with `username` or `email` containing "john", having the "Admin" or "Manager" role, and sorting by `email` in descending order:
   
   ```bash
   curl "http://127.0.0.1:5000/users?page=1&per_page=5&search=john&role=Admin,Manager&sort_by=email&sort_order=desc"
   ```

   #### 5. **Sort users by username**:
   
   To sort users by `username` in ascending order:
   
   ```bash
   curl "http://127.0.0.1:5000/users?page=1&per_page=5&sort_by=username&sort_order=asc"
   ```

### Explanation of `curl` commands:

- `page=1`: This specifies that the first page of results should be returned.
- `per_page=5`: This specifies that 5 results should be returned per page.
- `search=john`: This searches for users whose `username` or `email` contains "john".
- `role=Admin,Manager`: This filters users to only those who have either the "Admin" or "Manager" role.
- `sort_by=email`: This sorts the results by `email` in ascending order by default.
- `sort_order=desc`: This sorts the results in descending order.

### Example Response:

For a request like this:

```bash
curl "http://127.0.0.1:5000/users?page=1&per_page=5&search=john&role=Admin,Manager&sort_by=email&sort_order=desc"
```

You might receive a response like this:

```json
{
    "total": 10,
    "pages": 2,
    "current_page": 1,
    "per_page": 5,
    "users": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "roles": [
                {
                    "id": 1,
                    "name": "Admin"
                }
            ]
        },
        {
            "id": 2,
            "username": "john_smith",
            "email": "john.smith@example.com",
            "roles": [
                {
                    "id": 2,
                    "name": "Manager"
                }
            ]
        }
    ]
}
```

This means:
- The API returned 2 users from page 1 of 5 users per page.
- The users have "Admin" or "Manager" roles.
- The results are sorted by email in descending order.

### Notes:
- The database URI is currently set to use SQLite (`sqlite:///yourdatabase.db`). You can switch it to any other database (e.g., PostgreSQL, MySQL) as needed.
- Don't forget to create the database tables before starting your app by running the Flask application (it will create tables automatically if they don't exist).
