from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, case, and_, or_
from datetime import datetime

app = Flask(__name__)

# Configure the database (use your actual database URI here)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define User and Company models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    companies = db.relationship('Company', backref='user', lazy=True)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Endpoint to count users by gender
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
    company_name = request.args.get('company_name')  # mandatory filter by company name

    # If no company name is provided, return an error
    if not company_name:
        return jsonify({"message": "company_name filter is required"}), 400

    # Start the query and apply filters conditionally
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

    # Apply OR filter: search email or name
    if search := request.args.get('search'):
        filters.append(
            or_(
                User.email.like(f"%{search}%"),  # email filter
                User.name.like(f"%{search}%")  # name filter
            )
        )

    # Filter by company name (MANDATORY filter)
    filters.append(Company.name.like(f"%{company_name}%"))

    # Combine all filters with AND
    if filters:
        query = query.filter(and_(*filters))

    # Apply INNER JOIN between User and Company
    query = query.join(Company, User.id == Company.user_id)

    # Group by gender and execute the query
    query = query.group_by(User.gender).all()

    # Prepare the result
    result = {
        "total_users_by_gender": [
            {"gender": row[0], "count": row[1]} for row in query
        ],
        "users_by_gender_this_month": [
            {"gender": row[0], "count": row[2]} for row in query
        ]
    }

    return jsonify(result)


# Endpoint to insert a new user
@app.route('/insert_user', methods=['POST'])
def insert_user():
    data = request.get_json()

    # Extract user data from request
    name = data.get('name')
    email = data.get('email')
    age = data.get('age')
    gender = data.get('gender')

    # Check if required fields are present
    if not name or not email or not age or not gender:
        return jsonify({"message": "All fields (name, email, age, gender) are required"}), 400

    # Create a new user
    new_user = User(name=name, email=email, age=age, gender=gender)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User added successfully", "user_id": new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


# Endpoint to insert a company
@app.route('/insert_company', methods=['POST'])
def insert_company():
    data = request.get_json()

    # Extract company data from request
    company_name = data.get('company_name')
    user_id = data.get('user_id')

    # Check if required fields are present
    if not company_name or not user_id:
        return jsonify({"message": "Both company_name and user_id are required"}), 400

    # Check if the user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Create a new company
    new_company = Company(name=company_name, user_id=user_id)

    try:
        db.session.add(new_company)
        db.session.commit()
        return jsonify({"message": "Company added successfully", "company_id": new_company.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


# Initialize the database (just for the first time, or when you update models)
@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)