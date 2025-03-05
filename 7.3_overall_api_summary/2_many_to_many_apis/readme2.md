Certainly! Here are some CRUD API endpoints for adding users and roles, and assigning roles to users. These endpoints will allow you to populate the database for testing purposes.

### Full Code with CRUD APIs for Users, Roles, and User-Role Assignments:

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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'id', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)
    role_filter = request.args.get('role', '', type=str)

    query = db.session.query(User).join(UserRole, UserRole.user_id == User.id).join(Role, Role.id == UserRole.role_id)

    if search:
        query = query.filter(
            (User.username.like(f'%{search}%')) | 
            (User.email.like(f'%{search}%'))
        )

    if role_filter:
        roles = role_filter.split(',')
        role_filters = [Role.name.like(f'%{role.strip()}%') for role in roles]
        query = query.filter(or_(*role_filters))

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

    users = query.paginate(page, per_page, False)

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

# API endpoint to add a new user
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({'error': 'Username and email are required'}), 400

    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully', 'user': {'id': user.id, 'username': user.username, 'email': user.email}}), 201

# API endpoint to add a new role
@app.route('/roles', methods=['POST'])
def add_role():
    data = request.get_json()
    role_name = data.get('name')

    if not role_name:
        return jsonify({'error': 'Role name is required'}), 400

    role = Role(name=role_name)
    db.session.add(role)
    db.session.commit()

    return jsonify({'message': 'Role created successfully', 'role': {'id': role.id, 'name': role.name}}), 201

# API endpoint to assign a role to a user
@app.route('/users/<int:user_id>/roles', methods=['POST'])
def assign_role_to_user(user_id):
    data = request.get_json()
    role_id = data.get('role_id')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role not found'}), 404

    user.roles.append(role)
    db.session.commit()

    return jsonify({'message': 'Role assigned to user successfully'}), 200

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
```

### Explanation of CRUD Endpoints:

1. **`POST /users`**: Adds a new user to the `users` table.
   - **Request Body** (JSON):
     ```json
     {
         "username": "john_doe",
         "email": "john@example.com"
     }
     ```

2. **`POST /roles`**: Adds a new role to the `roles` table.
   - **Request Body** (JSON):
     ```json
     {
         "name": "Admin"
     }
     ```

3. **`POST /users/<user_id>/roles`**: Assigns a role to an existing user.
   - **Request Body** (JSON):
     ```json
     {
         "role_id": 1
     }
     ```

### Example `curl` Commands:

#### 1. **Create a new user**:
```bash
curl -X POST "http://127.0.0.1:5000/users" -H "Content-Type: application/json" -d '{"username": "john_doe", "email": "john@example.com"}'
```

#### 2. **Create a new role**:
```bash
curl -X POST "http://127.0.0.1:5000/roles" -H "Content-Type: application/json" -d '{"name": "Admin"}'
```

#### 3. **Assign a role to a user** (e.g., user with `id=1` gets role `id=1`):
```bash
curl -X POST "http://127.0.0.1:5000/users/1/roles" -H "Content-Type: application/json" -d '{"role_id": 1}'
```

#### 4. **Get users with roles (with pagination, searching, and filtering)**:
```bash
curl "http://127.0.0.1:5000/users?page=1&per_page=5&role=Admin&search=john"
```

### How to Test:

1. **Run the Flask App**:
   - Run your Flask app by executing the following command:
     ```bash
     python app.py
     ```

2. **Test with `curl`**:
   - Use the `curl` commands mentioned above to test adding users, roles, and assigning roles to users.

### Sample Responses:

1. **Create User Response**:
   ```json
   {
       "message": "User created successfully",
       "user": {
           "id": 1,
           "username": "john_doe",
           "email": "john@example.com"
       }
   }
   ```

2. **Create Role Response**:
   ```json
   {
       "message": "Role created successfully",
       "role": {
           "id": 1,
           "name": "Admin"
       }
   }
   ```

3. **Assign Role to User Response**:
   ```json
   {
       "message": "Role assigned to user successfully"
   }
   ```

### Conclusion:

You now have a set of CRUD APIs to create users, roles, and assign roles to users, as well as an API to retrieve users with pagination, searching, and filtering by roles. Use the `curl` commands to interact with the API and populate the database with data for testing.