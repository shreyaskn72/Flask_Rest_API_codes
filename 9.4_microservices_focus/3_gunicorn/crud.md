
---

## ✅ Single File Flask SQLite CRUD Example

### 📄 `app.py`

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQLite file-based database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Model definition
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

# Create the database
@app.before_first_request
def create_tables():
    db.create_all()

# Get all items
@app.route('/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items])

# Get one item
@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())

# Create a new item
@app.route('/items', methods=['POST'])
def create_item():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    item = Item(name=data['name'], description=data.get('description'))
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

# Update an item
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.json
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    db.session.commit()
    return jsonify(item.to_dict())

# Delete an item
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted'})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
```

---

## 📦 Install Requirements

```bash
pip install flask flask_sqlalchemy
```

---

## 🚀 Run the App

```bash
python app.py
```

Server will start at:
[http://localhost:5000](http://localhost:5000)

---

## 📋 Test It with `curl`

### ➕ Create an Item

```bash
curl -X POST http://localhost:5000/items \
-H "Content-Type: application/json" \
-d '{"name": "Notebook", "description": "A lined notebook"}'
```

### 📋 List All Items

```bash
curl http://localhost:5000/items
```

### 🔍 Get Single Item

```bash
curl http://localhost:5000/items/1
```

### ✏️ Update Item

```bash
curl -X PUT http://localhost:5000/items/1 \
-H "Content-Type: application/json" \
-d '{"name": "Updated", "description": "New description"}'
```

### ❌ Delete Item

```bash
curl -X DELETE http://localhost:5000/items/1
```

---


