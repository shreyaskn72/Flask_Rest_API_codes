Here's a full setup for a **Dockerized Flask API using Gunicorn and Nginx** — a common production architecture.

---

## ✅ What You Get

* Flask app (CRUD with SQLite)
* Gunicorn WSGI server (runs your Flask app)
* Nginx (reverse proxy, serves as the public entry point)
* Dockerized, clean, and production-ready

---

## 📁 Project Structure

```
flask_gunicorn_nginx/
├── app/
│   ├── app.py
│   ├── models.py
│   └── __init__.py
├── config.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── nginx/
    └── nginx.conf
```

---

## 🧱 1. Flask App (`app/app.py`)

```python
from flask import Flask, request, jsonify
from .models import db, Item

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify([item.to_dict() for item in Item.query.all()])

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())

@app.route('/items', methods=['POST'])
def create_item():
    data = request.json
    item = Item(name=data['name'], description=data.get('description'))
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.json
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    db.session.commit()
    return jsonify(item.to_dict())

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted'})
```

---

## 📦 2. Models (`app/models.py`)

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
```

---

## 📦 3. `app/__init__.py`

```python
from .app import app
```

---

## 📄 4. `requirements.txt`

```txt
Flask==2.2.2
Flask-SQLAlchemy==3.0.5
gunicorn==21.2.0
```

---

## 🐳 5. `Dockerfile`

```Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers=3"]
```

---

## 🌐 6. Nginx Config (`nginx/nginx.conf`)

```nginx
events {}

http {
    server {
        listen 80;

        location / {
            proxy_pass http://web:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

## 🐋 7. Docker Compose (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: flask_app
    volumes:
      - .:/app
    expose:
      - 8000
    depends_on:
      - nginx

  nginx:
    image: nginx:alpine
    container_name: nginx_proxy
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
```

---

## 🚀 8. Run It

```bash
docker-compose up --build
```

Open in your browser:

```bash
http://localhost/items
```

---

## 📋 API Endpoints

| Method | Endpoint      | Description     |
| ------ | ------------- | --------------- |
| GET    | `/items`      | List all items  |
| GET    | `/items/<id>` | Get item by ID  |
| POST   | `/items`      | Create new item |
| PUT    | `/items/<id>` | Update item     |
| DELETE | `/items/<id>` | Delete item     |

---

## ✅ Summary

| Component | Role                             |
| --------- | -------------------------------- |
| Flask     | Handles business logic (API)     |
| Gunicorn  | Runs the Flask app (WSGI server) |
| Nginx     | Serves HTTP, proxies to Gunicorn |
| SQLite    | Local DB storage                 |
| Docker    | Containers for all components    |

---


