from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case

app = Flask(__name__)

# Configure the database URI (using SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Define the Sales model
class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sales_amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Sales(id={self.id}, sales_amount={self.sales_amount})>"

# Initialize the database (run this once to create the tables)
@app.before_first_request
def create_tables():
    db.create_all()

# Route to insert sales data
@app.route('/insert_sales', methods=['POST'])
def insert_sales():
    data = request.get_json()
    sales_amount = data.get('sales_amount')

    if sales_amount is None:
        return jsonify({"message": "sales_amount is required"}), 400

    new_sale = Sales(sales_amount=sales_amount)
    db.session.add(new_sale)
    db.session.commit()
    return jsonify({"message": "Sale added successfully", "sale_id": new_sale.id}), 201

# Route to query sales data with a CASE statement using SQLAlchemy's case() function
@app.route('/sales_summary', methods=['GET'])
def sales_summary():
    # Use SQLAlchemy's case() construct to implement the CASE statement
    sales_category = case(
        [
            (Sales.sales_amount < 100, 'Low'),
            (Sales.sales_amount.between(100, 500), 'Medium'),
            (Sales.sales_amount > 500, 'High')
        ], else_='Unknown'
    )

    # Perform the query with the conditional logic (CASE)
    sales_data = db.session.query(
        Sales.sales_amount,
        sales_category.label('sales_category')
    ).all()

    # Convert the result to a list of dictionaries for JSON response
    result = [{"sales_amount": sale.sales_amount, "sales_category": sale.sales_category} for sale in sales_data]

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)