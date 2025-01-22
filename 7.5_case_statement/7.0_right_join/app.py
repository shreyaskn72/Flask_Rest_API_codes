from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, case
from datetime import datetime

app = Flask(__name__)

# Configure the database URI (use your actual database URI)
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

# Endpoint: Right Join and Group by Company with User Count and Gender Grouping
@app.route('/company_user_right_join_grouped', methods=['GET'])
def company_user_right_join_grouped():
    # Query the companies and right join with the User table
    query = db.session.query(
        Company.id.label('company_id'),
        Company.name.label('company_name'),
        func.count(User.id).label('user_count'),
        func.sum(case(
            [(User.gender == 'Male', 1)],
            else_=0
        )).label('male_count'),
        func.sum(case(
            [(User.gender == 'Female', 1)],
            else_=0
        )).label('female_count'),
        func.sum(case(
            [(User.gender == 'Other', 1)],
            else_=0
        )).label('other_count')
    )

    # Perform the RIGHT JOIN, ensuring all companies are included even if no users are associated
    query = query.join(User, User.id == Company.user_id, isouter=True)  # RIGHT JOIN with `isouter=True`

    # Group by company to get the count of users and gender-specific counts
    query = query.group_by(Company.id, Company.name)

    # Execute the query and fetch all results
    results = query.all()

    # Prepare the response data
    response = []
    for row in results:
        response.append({
            "company_id": row.company_id,
            "company_name": row.company_name,
            "user_count": row.user_count,
            "male_count": row.male_count,
            "female_count": row.female_count,
            "other_count": row.other_count
        })

    return jsonify(response)

# Insert a new user
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

# Insert a new company
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