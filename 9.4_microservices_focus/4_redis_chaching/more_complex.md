A **hybrid caching approach** gives you the **best of both worlds**:

* Use `flask_caching` for simple view-level caching (declarative, fast setup).
* Use `redis-py` for more **granular control** (e.g., caching parts of responses, tagging, or custom invalidation logic).

---

## ✅ Setup

### Install both:

```bash
pip install flask flask_sqlalchemy Flask-Caching redis
```

---

## 🚀 Hybrid Caching in `app.py`

Below is a working example where:

* **`flask_caching`** caches `/employees/high-salary` (simple, auto-TTL).
* **`redis-py`** handles `/employees/top2-by-department` (custom logic, manual cache).

---

### 🔧 `app.py` (with hybrid caching)

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from sqlalchemy import func
import redis
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Caching config (for simple caching)
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

db = SQLAlchemy(app)
cache = Cache(app)

# Redis-py client (for advanced caching)
r = redis.Redis(host='localhost', port=6379, db=0)

# Employee model
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

# Create tables
with app.app_context():
    db.create_all()

# Utility: Clear all caches
def clear_employee_cache():
    cache.delete('high_salary_emps')
    r.delete('top2_by_dept')

# CREATE
@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.json
    new_emp = Employee(**data)
    db.session.add(new_emp)
    db.session.commit()
    clear_employee_cache()
    return jsonify(new_emp.to_dict()), 201

# READ all
@app.route('/employees', methods=['GET'])
def get_employees():
    emps = Employee.query.all()
    return jsonify([e.to_dict() for e in emps])

# READ single
@app.route('/employees/<int:id>', methods=['GET'])
def get_employee(id):
    emp = Employee.query.get_or_404(id)
    return jsonify(emp.to_dict())

# UPDATE
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

# DELETE
@app.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    clear_employee_cache()
    return jsonify({'message': 'Deleted'}), 200

# Cached via flask_caching
@app.route('/employees/high-salary', methods=['GET'])
@cache.cached(key_prefix='high_salary_emps')
def high_salary_employees():
    emps = Employee.query.filter(Employee.salary > 100000).all()
    return jsonify([e.to_dict() for e in emps])

# Custom Redis-py caching for complex logic
@app.route('/employees/top2-by-department', methods=['GET'])
def top_two_by_department():
    cache_key = 'top2_by_dept'
    cached_data = r.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data))

    # Not cached, compute manually
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

    result = db.session.query(subquery).filter(subquery.c.rank <= 2).all()
    output = [
        {
            'id': row.id,
            'name': row.name,
            'salary': row.salary,
            'department': row.department
        }
        for row in result
    ]

    # Cache it with Redis-py
    r.set(cache_key, json.dumps(output), ex=300)
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 🔍 Why This Hybrid Approach Works

| Route                           | Cache Method    | Why?                                                    |
| ------------------------------- | --------------- | ------------------------------------------------------- |
| `/employees/high-salary`        | `flask_caching` | Simple data, easy TTL                                   |
| `/employees/top2-by-department` | `redis-py`      | Custom cache key, manual control, flexible invalidation |

You can now:

* Control TTL or structure manually (with `redis-py`)
* Still use decorators for fast view caching (`flask_caching`)

---

