from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case, func

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

# New route to count sales by category (Low, Medium, High)
@app.route('/sales_count_by_category', methods=['GET'])
def sales_count_by_category():
    # Define the CASE statement for categorization
    sales_category = case(
        [
            (Sales.sales_amount < 100, 'Low'),
            (Sales.sales_amount.between(100, 500), 'Medium'),
            (Sales.sales_amount > 500, 'High')
        ], else_='Unknown'
    )

    # Perform the aggregation to count sales in each category
    sales_counts = db.session.query(
        sales_category.label('category'),
        func.count().label('count')
    ).group_by(sales_category).all()

    # Convert the result to a dictionary for JSON response
    result = [{"category": row.category, "count": row.count} for row in sales_counts]

    return jsonify(result)


# New route to count overall sales and sales by category (Low, Medium, High)
@app.route('/sales_count_by_category_with_total', methods=['GET'])
def sales_count_by_category_with_total():
        # Define the CASE statement for categorizing sales_amount
        sales_category = case(
            [
                (Sales.sales_amount < 100, 'Low'),
                (Sales.sales_amount.between(100, 500), 'Medium'),
                (Sales.sales_amount > 500, 'High')
            ], else_='Unknown'
        )

        # Perform the aggregation to count overall sales and sales in each category in one query
        sales_counts = db.session.query(
            func.count().label('overall_sales_count'),  # Count of all sales
            func.sum(case([(sales_category == 'Low', 1)], else_=0)).label('Low_count'),
            func.sum(case([(sales_category == 'Medium', 1)], else_=0)).label('Medium_count'),
            func.sum(case([(sales_category == 'High', 1)], else_=0)).label('High_count')
        ).first()  # Use `.first()` to get the tuple of counts

        # Extract values from the result tuple
        overall_sales_count = sales_counts.overall_sales_count
        low_count = sales_counts.Low_count
        medium_count = sales_counts.Medium_count
        high_count = sales_counts.High_count

        # Convert the result into a structured response
        result = {
            "overall_sales_count": overall_sales_count,
            "sales_by_category": {
                "Low": low_count,
                "Medium": medium_count,
                "High": high_count
            }
        }

        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)