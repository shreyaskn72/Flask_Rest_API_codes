from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, case
from datetime import datetime

app = Flask(__name__)

# Configure the database URI (using SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)


# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, age={self.age}, gender={self.gender}, email={self.email}, created_on={self.created_on})>"


# Initialize the database (run this once to create the tables)
@app.before_first_request
def create_tables():
    db.create_all()


# Route to insert a new user
@app.route('/insert_user', methods=['POST'])
def insert_user():
    data = request.get_json()

    # Ensure all required fields are provided
    name = data.get('name')
    age = data.get('age')
    gender = data.get('gender')
    email = data.get('email')

    if not name or not age or not gender or not email:
        return jsonify({"message": "Missing required fields: name, age, gender, email"}), 400

    # Create a new user and add to the session
    new_user = User(name=name, age=age, gender=gender, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user_id": new_user.id}), 201


# Route to get count of users by gender and count of users by gender created in this month, with filters
@app.route('/user_count_by_gender', methods=['GET'])
def user_count_by_gender():
    # Get the current date and month
    current_date = datetime.utcnow()
    current_month = current_date.month
    current_year = current_date.year

    # Get query parameters for filtering
    email = request.args.get('email')  # optional filter by email
    age = request.args.get('age', type=int)  # optional filter by age

    # Start the query and apply filters based on query params
    query = db.session.query(
        User.gender,
        func.count(User.id).label('total_users_count'),
        func.sum(
            case(
                [
                    (
                        (func.extract('month', User.created_on) == current_month) &
                        (func.extract('year', User.created_on) == current_year), 1
                    )
                ],
                else_=0
            ).label('users_created_this_month')
        )
    )

    # Apply filters if provided
    if email:
        query = query.filter(User.email == email)

    if age:
        query = query.filter(User.age == age)

    query = query.group_by(User.gender).all()

    # Prepare the result, ensuring we're using the correct label names
    result = {
        "total_users_by_gender": [
            {"gender": row[0], "count": row[1]} for row in query
        ],
        "users_by_gender_this_month": [
            {"gender": row[0], "count": row[2]} for row in query
        ]
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)