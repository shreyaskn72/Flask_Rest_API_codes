let’s walk through a **complete simple Flask + Celery + RabbitMQ setup** with full code, clear explanations, and exact commands to run it.

---

## ✅ Simple Folder Structure

```
simple_celery_project/
├── app.py
├── tasks.py
├── celery_app.py
├── config.py
├── beat_schedule.py
├── requirements.txt
└── start.sh
```

---

## 📦 1. `requirements.txt`

```txt
Flask==2.2.2
Celery==5.2.7
requests==2.28.1
flower==1.2.0
```

### 🔧 Install all dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ 2. `config.py`

Holds centralized configuration.

```python
class Config:
    CELERY_BROKER_URL = 'amqp://localhost'
    CELERY_RESULT_BACKEND = 'rpc://'
```

* **Broker**: RabbitMQ (running on localhost)
* **Backend**: Stores result temporarily (here, RPC backend)

---

## 🔧 3. `celery_app.py`

Sets up and returns the Celery instance.

```python
from celery import Celery
from config import Config
from beat_schedule import beat_schedule

def make_celery():
    celery = Celery(
        'simple_project',
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=['tasks']
    )
    celery.conf.timezone = 'UTC'
    celery.conf.beat_schedule = beat_schedule
    return celery

celery = make_celery()
```

---

## ⏰ 4. `beat_schedule.py`

Schedules periodic tasks.

```python
from celery.schedules import crontab

beat_schedule = {
    'call-api-every-minute': {
        'task': 'tasks.call_api',
        'schedule': crontab(minute='*/1'),  # every minute
    },
}
```

---

## 🧠 5. `tasks.py`

Defines the Celery task.

```python
from celery_app import celery
import requests

@celery.task
def call_api():
    try:
        response = requests.get("https://api.publicapis.org/entries")
        print("API call successful.")
        return response.json()
    except Exception as e:
        print(f"API call failed: {e}")
        return {'error': str(e)}
```

---

## 🌐 6. `app.py`

Flask app to trigger or check background task.

```python
from flask import Flask, jsonify
from tasks import call_api

app = Flask(__name__)

@app.route('/trigger-task', methods=['GET'])
def trigger_task():
    task = call_api.delay()
    return jsonify({'task_id': task.id}), 202

@app.route('/task-status/<task_id>', methods=['GET'])
def get_status(task_id):
    result = call_api.AsyncResult(task_id)
    return jsonify({
        'status': result.state,
        'result': result.result if result.ready() else None
    })

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 🖥️ 7. `start.sh`

Script to launch Flask, Celery worker, Celery beat, and Flower in new terminals (Linux/macOS with `gnome-terminal`):

```bash
#!/bin/bash

PROJECT_DIR="$(pwd)"

echo "Starting Flask app..."
gnome-terminal -- bash -c "cd $PROJECT_DIR && python app.py; exec bash"

sleep 1

echo "Starting Celery worker..."
gnome-terminal -- bash -c "cd $PROJECT_DIR && celery -A celery_app.celery worker --loglevel=info; exec bash"

sleep 1

echo "Starting Celery Beat..."
gnome-terminal -- bash -c "cd $PROJECT_DIR && celery -A celery_app.celery beat --loglevel=info; exec bash"

sleep 1

echo "Starting Flower monitoring..."
gnome-terminal -- bash -c "cd $PROJECT_DIR && flower -A celery_app.celery --port=5555; exec bash"

echo "✅ All services launched."
```

Make it executable:

```bash
chmod +x start.sh
```

Run it:

```bash
./start.sh
```

---

## 🚀 Manual Commands (If you want to run them one by one)

### 1. Start Flask:

```bash
python app.py
```

### 2. Start Celery worker:

```bash
celery -A celery_app.celery worker --loglevel=info
```

### 3. Start Celery beat:

```bash
celery -A celery_app.celery beat --loglevel=info
```

### 4. Start Flower:

```bash
flower -A celery_app.celery --port=5555
```

Visit [http://localhost:5555](http://localhost:5555) to see Flower dashboard.

---

## 🔍 Testing the Setup

### 🔹 Trigger a background task:

```bash
curl http://localhost:5000/trigger-task
```

### 🔹 Check the status:

```bash
curl http://localhost:5000/task-status/<task_id>
```

Replace `<task_id>` with the ID from the previous response.

---

## 🧠 What You Just Built

| Component                            | Role                          |
| ------------------------------------ | ----------------------------- |
| Flask (`app.py`)                     | Sends and checks tasks        |
| Celery (`celery_app.py`, `tasks.py`) | Executes tasks asynchronously |
| RabbitMQ                             | Message broker (queue)        |
| Beat                                 | Schedules repeating tasks     |
| Flower                               | Dashboard to monitor tasks    |

---
