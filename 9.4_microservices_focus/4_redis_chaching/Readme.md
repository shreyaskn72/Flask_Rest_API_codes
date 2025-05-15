Here is a single-file Flask app (`app.py`) that includes:

✅ Basic CRUD operations
✅ API to get employees with salary > 100,000
✅ API to get top 2 highest-paid employees **per department**

---

### ✅ Final `app.py`

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Employee Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    department = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'salary': self.salary,
            'department': self.department
        }

# Create DB
with app.app_context():
    db.create_all()

# CREATE employee
@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.json
    new_emp = Employee(
        name=data['name'],
        salary=data['salary'],
        department=data['department']
    )
    db.session.add(new_emp)
    db.session.commit()
    return jsonify(new_emp.to_dict()), 201

# READ all employees
@app.route('/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    return jsonify([emp.to_dict() for emp in employees])

# READ single employee
@app.route('/employees/<int:id>', methods=['GET'])
def get_employee(id):
    emp = Employee.query.get_or_404(id)
    return jsonify(emp.to_dict())

# UPDATE employee
@app.route('/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    emp = Employee.query.get_or_404(id)
    data = request.json
    emp.name = data.get('name', emp.name)
    emp.salary = data.get('salary', emp.salary)
    emp.department = data.get('department', emp.department)
    db.session.commit()
    return jsonify(emp.to_dict())

# DELETE employee
@app.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'}), 200

# Get employees with salary > 100000
@app.route('/employees/high-salary', methods=['GET'])
def high_salary_employees():
    employees = Employee.query.filter(Employee.salary > 100000).all()
    return jsonify([emp.to_dict() for emp in employees])

# Get top 2 earners per department
@app.route('/employees/top2-by-department', methods=['GET'])
def top_two_by_department():
    subquery = (
        db.session.query(
            Employee.id,
            Employee.name,
            Employee.salary,
            Employee.department,
            func.rank().over(
                partition_by=Employee.department,
                order_by=Employee.salary.desc()
            ).label('rank')
        ).subquery()
    )

    top_emps = db.session.query(
        subquery
    ).filter(subquery.c.rank <= 2).all()

    result = []
    for row in top_emps:
        result.append({
            'id': row.id,
            'name': row.name,
            'salary': row.salary,
            'department': row.department,
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

---

### 🧪 Example Request (using cURL or Postman)

#### Create Employee:

```bash
curl -X POST http://localhost:5000/employees -H "Content-Type: application/json" -d '{"name": "Alice", "salary": 70000, "department": "Engineering"}'
```

### 🧪 Test Routes

* `POST /employees` – Create employee
* `GET /employees` – List all employees
* `GET /employees/<id>` – Get single employee
* `PUT /employees/<id>` – Update employee
* `DELETE /employees/<id>` – Delete employee
* `GET /employees/high-salary` – All employees with salary > 100000
* `GET /employees/top2-by-department` – Top 2 highest-paid employees per department

---





It's **a good idea** to use **caching** for the `/employees/high-salary` and `/employees/top2-by-department` APIs since:

* These endpoints are **read-heavy**.
* The data likely doesn't change frequently (only when an employee is added or updated).
* You want to **reduce database load** and improve **response time**.

---

## ✅ Why Redis for Caching?

* It's fast (in-memory).
* Ideal for **frequently accessed, infrequently updated** data.
* Integrates well with Flask using libraries like `Flask-Caching`.

---

## ✅ Best Caching Strategy

We’ll use the **cache-aside pattern**:

* Try to get data from Redis.
* If not found (cache miss), query the database, store the result in Redis, and return it.
* On write operations (POST/PUT/DELETE), **invalidate the relevant cache keys**.

---

## 🔧 Requirements

Install necessary packages:

```bash
pip install flask flask_sqlalchemy redis Flask-Caching
```

Make sure Redis server is running locally (or connect to a cloud Redis URL if remote).

---

## 🚀 Updated `app.py` with Redis Caching

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Redis cache config
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # cache timeout in seconds

db = SQLAlchemy(app)
cache = Cache(app)

# Employee Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    department = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'salary': self.salary,
            'department': self.department
        }

# Create DB
with app.app_context():
    db.create_all()

# Utility: Invalidate cache on data mutation
def clear_employee_cache():
    cache.delete('high_salary_emps')
    cache.delete('top2_by_dept')

# CREATE employee
@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.json
    new_emp = Employee(
        name=data['name'],
        salary=data['salary'],
        department=data['department']
    )
    db.session.add(new_emp)
    db.session.commit()
    clear_employee_cache()
    return jsonify(new_emp.to_dict()), 201

# READ all employees
@app.route('/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    return jsonify([emp.to_dict() for emp in employees])

# READ single employee
@app.route('/employees/<int:id>', methods=['GET'])
def get_employee(id):
    emp = Employee.query.get_or_404(id)
    return jsonify(emp.to_dict())

# UPDATE employee
@app.route('/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    emp = Employee.query.get_or_404(id)
    data = request.json
    emp.name = data.get('name', emp.name)
    emp.salary = data.get('salary', emp.salary)
    emp.department = data.get('department', emp.department)
    db.session.commit()
    clear_employee_cache()
    return jsonify(emp.to_dict())

# DELETE employee
@app.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    clear_employee_cache()
    return jsonify({'message': 'Deleted successfully'}), 200

# Cached: Get employees with salary > 100000
@app.route('/employees/high-salary', methods=['GET'])
@cache.cached(key_prefix='high_salary_emps')
def high_salary_employees():
    employees = Employee.query.filter(Employee.salary > 100000).all()
    return jsonify([emp.to_dict() for emp in employees])

# Cached: Top 2 highest paid per department
@app.route('/employees/top2-by-department', methods=['GET'])
@cache.cached(key_prefix='top2_by_dept')
def top_two_by_department():
    subquery = (
        db.session.query(
            Employee.id,
            Employee.name,
            Employee.salary,
            Employee.department,
            func.rank().over(
                partition_by=Employee.department,
                order_by=Employee.salary.desc()
            ).label('rank')
        ).subquery()
    )

    top_emps = db.session.query(subquery).filter(subquery.c.rank <= 2).all()

    result = [{
        'id': row.id,
        'name': row.name,
        'salary': row.salary,
        'department': row.department
    } for row in top_emps]

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 🔁 How It Works

* ✅ On first API call, data is queried from the DB and cached in Redis.
* ✅ On subsequent calls, data is served from Redis instantly.
* 🔄 When an employee is created, updated, or deleted, the related cache keys are invalidated using `clear_employee_cache()`.

---