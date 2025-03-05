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

#left join users
@app.route('/left_join/users', methods=['GET'])
def get_users_lef_join():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'id', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)
    role_filter = request.args.get('role', '', type=str)

    # Using LEFT JOIN to include users without roles
    query = db.session.query(User).join(UserRole, UserRole.user_id == User.id, isouter=True).join(Role, Role.id == UserRole.role_id, isouter=True)

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
            'roles': [{'id': role.id, 'name': role.name} for role in user.roles] if user.roles else []
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