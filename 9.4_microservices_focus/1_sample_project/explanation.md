Here's the full project with the inclusion of **`common/utils.py`** to handle the event publishing logic. This will centralize the functionality and make the project more maintainable.

---

### **Complete Project Structure:**

```
/microservices
  /user_service
    /app.py
    /models.py
    /config.py
    /init_db.py
  /order_service
    /app.py
    /models.py
    /config.py
  /reporting_service
    /app.py
    /models.py
    /config.py
    /init_db.py
  /common
    /utils.py  # Shared utilities like RabbitMQ event publishing
  /docker-compose.yml
```

---

### **Step 1: Create the `common/utils.py`**

This file will contain shared functionality, specifically for publishing events to RabbitMQ.

#### **`common/utils.py`**

```python
import pika
import json

def publish_event(queue_name, event_data):
    """
    Publish an event to a RabbitMQ queue.

    :param queue_name: The name of the RabbitMQ queue to publish the event to.
    :param event_data: The data to send to the queue, typically a dict.
    """
    # RabbitMQ connection setup
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    # Ensure the queue exists
    channel.queue_declare(queue=queue_name)

    # Publish the event data as a JSON string
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(event_data)
    )
    print(f"[✓] Event published to {queue_name}")
    
    # Close the connection
    connection.close()
```

---

### **Step 2: User Service**

#### **`user_service/config.py`**

```python
DATABASE_URL = "sqlite:///user_service.db"
```

#### **`user_service/models.py`**

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
```

#### **`user_service/app.py`**

```python
from flask import Flask, request, jsonify
from config import DATABASE_URL
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"id": new_user.id, "name": new_user.name, "email": new_user.email}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5001)
```

#### **`user_service/init_db.py`**

```python
from models import db
from app import app

with app.app_context():
    db.create_all()
```

---

### **Step 3: Order Service**

#### **`order_service/config.py`**

```python
DATABASE_URL = "sqlite:///order_service.db"
```

#### **`order_service/models.py`**

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    item = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
```

#### **`order_service/app.py`**

```python
from flask import Flask, request, jsonify
from config import DATABASE_URL
from models import db, Order
from common.utils import publish_event  # Import the shared utility function

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    new_order = Order(user_id=data['user_id'], item=data['item'], amount=data['amount'])
    db.session.add(new_order)
    db.session.commit()

    # Event data to be sent
    event_data = {
        "event_type": "OrderCreated",
        "user_id": new_order.user_id,
        "amount": new_order.amount
    }

    # Publish the event using the shared utility
    publish_event('order_events', event_data)

    return jsonify({"id": new_order.id, "user_id": new_order.user_id, "item": new_order.item, "amount": new_order.amount}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5002)
```

---

### **Step 4: Reporting Service**

#### **`reporting_service/config.py`**

```python
DATABASE_URL = "sqlite:///reporting_service.db"
```

#### **`reporting_service/models.py`**

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserOrderSummary(db.Model):
    __tablename__ = "user_order_summary"

    user_id = db.Column(db.String, primary_key=True)
    total_spent = db.Column(db.Float, default=0.0)
    order_count = db.Column(db.Integer, default=0)
```

#### **`reporting_service/app.py`**

```python
from flask import Flask, jsonify
from config import DATABASE_URL
from models import db, UserOrderSummary
import pika
import json
from common.utils import publish_event  # Shared utility import

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Setup RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='order_events')

def callback(ch, method, properties, body):
    event = json.loads(body)
    if event["event_type"] != "OrderCreated":
        return

    user_id = str(event["user_id"])
    amount = float(event["amount"])

    # Update or insert order summary into the database
    summary = UserOrderSummary.query.get(user_id)
    if summary:
        summary.total_spent += amount
        summary.order_count += 1
    else:
        summary = UserOrderSummary(user_id=user_id, total_spent=amount, order_count=1)
        db.session.add(summary)

    try:
        db.session.commit()
        print(f"[✓] Updated DB summary for user {user_id}")
    except Exception as e:
        db.session.rollback()
        print(f"[!] DB error: {e}")

# API to get top spenders
@app.route('/top_spenders', methods=['GET'])
def top_spenders():
    top_users = UserOrderSummary.query.order_by(UserOrderSummary.total_spent.desc()).limit(5).all()
    result = [{"user_id": user.user_id, "total_spent": user.total_spent, "order_count": user.order_count} for user in top_users]
    return jsonify(result)

# Start consuming messages
def start_consuming():
    channel.basic_consume(queue='order_events', on_message_callback=callback, auto_ack=True)
    print('[*] Waiting for events. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    start_consuming()
    app.run(port=5003)
```

#### **`reporting_service/init_db.py`**

```python
from models import db
from app import app

with app.app_context():
    db.create_all()
```

---

### **Step 5: Docker Compose (Optional)**

To simplify running the services together, you can use **Docker Compose** to set up RabbitMQ, User Service, Order Service, and Reporting Service.

#### **`docker-compose.yml`**

```yaml
version: "3.7"

services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"

  user_service:
    build: ./user_service
    ports:
      - "5001:5001"

  order_service:
    build: ./order_service
    ports:
      - "5002:5002"

  reporting_service:
    build: ./reporting_service
    ports:
      - "5003:5003"
```

### **Step 6: Running the Project**

1. **Start RabbitMQ**:

   * If you're using Docker Compose, just run:

     ```bash
     docker-compose up
     ```

   * Or manually start RabbitMQ using:

     ```bash
     docker run -d --hostname my-rabbit --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
     ```

2. **Initialize Databases**:

   * Run `init_db.py` in the `user_service` and `reporting_service` folders to create the initial SQLite databases.

3. **Run the Services**:

   * Run each service (`user_service`, `order_service`, `reporting_service`) using `python app.py` or Docker if you're using Docker Compose.

---

### **Step 7: Testing the System**

1. **Create Users**:

   ```bash
   curl -X POST http://localhost:5001/users \
     -H "Content-Type: application/json" \
     -d '{"name": "Alice", "email": "alice@example.com"}'
   ```

2. **Create Orders**:

   ```bash
   curl -X POST http://localhost:5002/orders \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "item": "Laptop", "amount": 1500.00}'
   ```

3. **Get Top Spenders**:

   ```bash
   curl http://localhost:5003/top_spenders
   ```

---

### **Conclusion**

Now, you have a **fully-functional microservices system** with:

* **User Service**: Manages users.
* **Order Service**: Manages orders and emits events.
* **Reporting Service**: Listens to events and calculates spending.

**`common/utils.py`** centralizes shared code for publishing RabbitMQ events, making your project more maintainable. Let me know if you need further refinements or additions!
