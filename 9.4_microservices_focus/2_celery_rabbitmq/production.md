Here's a **production-style setup** for a Flask project that uses:

* **Celery** for async/background tasks
* **Celery Beat** for periodic tasks
* **RabbitMQ** as the message broker
* **Flower** to monitor Celery tasks
* **Modular code structure** (separated config, celery app, tasks, etc.)

---

## 🏗️ Folder Structure

```
flask_celery_project/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── tasks.py
├── celery_app/
│   ├── __init__.py
│   ├── celery_worker.py
│   ├── config.py
│   └── beat_schedule.py
├── run.py
├── requirements.txt
└── README.md
```

---

## 🧾 1. `requirements.txt`

```txt
Flask==2.2.2
Celery==5.2.7
requests==2.28.1
flower==1.2.0
```

Install:

```bash
pip install -r requirements.txt
```

---

## ⚙️ 2. `celery_app/config.py`

```python
class Config:
    CELERY_BROKER_URL = 'amqp://localhost'           # RabbitMQ
    CELERY_RESULT_BACKEND = 'rpc://'                 # Optional: can be Redis, DB, etc.
```

---

## 🔧 3. `celery_app/celery_worker.py`

```python
from celery import Celery
from celery_app.config import Config

def make_celery():
    celery = Celery(
        'flask_celery_project',
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=['app.tasks']
    )
    celery.conf.timezone = 'UTC'
    
    try:
        from celery_app.beat_schedule import beat_schedule
        celery.conf.beat_schedule = beat_schedule
    except ImportError:
        pass

    return celery

celery = make_celery()
```

---

## ⏰ 4. `celery_app/beat_schedule.py`

```python
from celery.schedules import crontab

beat_schedule = {
    'call-api-every-minute': {
        'task': 'app.tasks.call_api',
        'schedule': crontab(minute='*/1'),
    },
}
```

---

## 🚀 5. `app/tasks.py`

```python
from celery_app.celery_worker import celery
import requests

@celery.task
def call_api():
    try:
        response = requests.get('https://api.publicapis.org/entries')
        print("API call successful.")
        return response.json()
    except Exception as e:
        print(f"Error calling API: {e}")
        return {'error': str(e)}
```

---

## 🌐 6. `app/routes.py`

```python
from flask import Blueprint, jsonify
from app.tasks import call_api

bp = Blueprint('main', __name__)

@bp.route('/trigger-task', methods=['GET'])
def trigger_task():
    task = call_api.delay()
    return jsonify({"task_id": task.id}), 202

@bp.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    result = call_api.AsyncResult(task_id)
    return jsonify({
        "state": result.state,
        "result": result.result if result.ready() else None
    })
```

---

## 🧩 7. `app/__init__.py`

```python
from flask import Flask
from app.routes import bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app
```

---

## 🏃 8. `run.py`

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

---

## ✅ Final Commands to Run All Components

Ensure RabbitMQ is running (install via apt or brew, then `sudo systemctl start rabbitmq-server` or `brew services start rabbitmq`).

### ▶️ Start Flask App

```bash
python run.py
```

---

### ⚙️ Start Celery Worker

```bash
celery -A celery_app.celery_worker.celery worker --loglevel=info
```

---

### ⏰ Start Celery Beat (for scheduled tasks)

```bash
celery -A celery_app.celery_worker.celery beat --loglevel=info
```

---

### 📊 Start Flower Dashboard (monitoring)

```bash
flower -A celery_app.celery_worker.celery --port=5555
```

Then visit: [http://localhost:5555](http://localhost:5555)

---

## 🔍 Test the Setup

1. **Trigger a task manually**:

```bash
curl http://localhost:5000/trigger-task
```

2. **Check status**:

```bash
curl http://localhost:5000/task-status/<task_id>
```

3. **View periodic tasks**:
   Wait a minute and check Flower to see tasks being triggered automatically by Beat.

---

## 📚 Summary

| Component  | Role                        |
| ---------- | --------------------------- |
| `Flask`    | Web server to trigger tasks |
| `Celery`   | Executes background jobs    |
| `Beat`     | Schedules recurring tasks   |
| `RabbitMQ` | Broker for passing tasks    |
| `Flower`   | Web-based monitoring UI     |

---