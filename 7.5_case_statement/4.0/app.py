from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, case, and_, or_
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
    age_min = request.args.get('age_min', type=int)  # optional filter by minimum age
    age_max = request.args.get('age_max', type=int)  # optional filter by maximum age
    gender = request.args.get('gender')  # optional filter by gender
    created_this_month = request.args.get('created_this_month', type=bool)  # filter by users created in this month
    search = request.args.get('search')  # optional filter by email or name (OR condition)

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

    # Apply filters conditionally
    filters = []

    # Filter by email (exact match or partial match using LIKE)
    if email:
        filters.append(User.email.like(f"%{email}%"))

    # Filter by age range (greater than age_min and/or less than age_max)
    if age_min:
        filters.append(User.age >= age_min)
    if age_max:
        filters.append(User.age <= age_max)

    # Filter by gender
    if gender:
        filters.append(User.gender == gender)

    # Filter by users created in the current month
    if created_this_month is not None:
        if created_this_month:
            filters.append(
                and_(
                    func.extract('month', User.created_on) == current_month,
                    func.extract('year', User.created_on) == current_year
                )
            )

    # Apply OR filter: search email or name
    if search:
        filters.append(
            or_(
                User.email.like(f"%{search}%"),  # email filter
                User.name.like(f"%{search}%")  # name filter
            )
        )

    # Combine all filters with AND
    if filters:
        query = query.filter(and_(*filters))

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