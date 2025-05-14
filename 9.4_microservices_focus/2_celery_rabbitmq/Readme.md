# ✅ Flask + Celery + RabbitMQ + Beat + Flower (No Docker)

This guide helps you integrate:

* ✅ **Flask** for a simple web API
* ✅ **Celery** for background task processing
* ✅ **Celery Beat** for scheduling tasks
* ✅ **RabbitMQ** as a message broker
* ✅ **Flower** for real-time monitoring

---

## 📁 1. Project Structure

```
flask_celery_project/
│
├── app.py               # Flask web app
├── celery_app.py        # Celery factory setup
├── tasks.py             # Celery task(s)
├── beat_schedule.py     # Optional: periodic task config
├── config.py            # Central configuration
├── requirements.txt     # Python package dependencies
└── run_commands.txt     # (Optional) How to run each part
```

---

## 🧩 2. Installation & Setup

### 🐇 Install RabbitMQ

#### On **Linux**:

```bash
sudo apt install rabbitmq-server
sudo systemctl start rabbitmq-server
```

#### On **macOS**:

```bash
brew install rabbitmq
brew services start rabbitmq
```

#### On **Windows**:

Download and install from [https://www.rabbitmq.com/download.html](https://www.rabbitmq.com/download.html)

After installation, access the dashboard at:
**[http://localhost:15672](http://localhost:15672)**
(default user: `guest`, password: `guest`)

---

### 🐍 Install Python Dependencies

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install flask celery requests flower
```

Or use:

```bash
pip install -r requirements.txt
```

---

## ⚙️ 3. `config.py`

Central configuration for Celery:

```python
class Config:
    CELERY_BROKER_URL = 'pyamqp://guest@localhost//'
    CELERY_RESULT_BACKEND = 'rpc://'
```

---

## 🔧 4. `celery_app.py`

Factory to create and configure Celery:

```python
from celery import Celery
from config import Config

def make_celery():
    celery = Celery(
        'flask_celery_project',
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=['tasks']
    )
    celery.conf.timezone = 'UTC'
    return celery

celery = make_celery()
```

---

## 🌐 5. `app.py`

Simple Flask app with a route to trigger a task:

```python
from flask import Flask
from tasks import call_microservice

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask + Celery + RabbitMQ is running!"

@app.route('/trigger')
def trigger_task():
    call_microservice.delay()
    return "Task triggered!"
```

---

## 🧠 6. `tasks.py`

The actual Celery task calling a microservice (simulated):

```python
from celery_app import celery
import requests

@celery.task
def call_microservice():
    print("Calling microservice...")
    response = requests.get("https://httpbin.org/get")  # Replace with your real API
    print("Microservice responded with:", response.status_code)
    return response.status_code
```

---

## ⏰ 7. (Optional) `beat_schedule.py`

Adds periodic task scheduling to call the microservice daily.

```python
from celery.schedules import crontab
from celery_app import celery
from tasks import call_microservice

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run daily at midnight (UTC)
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        call_microservice.s(),
        name='Call microservice every day'
    )
```

You can skip this file and put this logic inside `celery_app.py` if you prefer.

---

## 🧪 8. How to Run (No Docker)

> Open **4 terminal tabs/windows** or use `start.sh`.

### Terminal 1: Run Flask

```bash
source venv/bin/activate        # Windows: venv\Scripts\activate
export FLASK_APP=app.py         # Windows: set FLASK_APP=app.py
flask run
```

### Terminal 2: Start Celery Worker

```bash
source venv/bin/activate
celery -A celery_app.celery worker --loglevel=info
```

### Terminal 3: Start Celery Beat (optional for scheduled tasks)

```bash
source venv/bin/activate
celery -A celery_app.celery beat --loglevel=info
```

### Terminal 4: Start Flower (monitoring)

```bash
source venv/bin/activate
celery -A celery_app.celery flower --port=5555
```

Then open [http://localhost:5555](http://localhost:5555) to view task status and worker health.

---

## 🔄 Full Flow Summary

1. 🧑 User accesses **[http://localhost:5000/trigger](http://localhost:5000/trigger)** → triggers the `call_microservice` task.
2. 📬 Task is sent to **RabbitMQ**.
3. ⚙️ **Celery Worker** picks up and runs the task asynchronously.
4. ⏰ **Celery Beat** can also trigger the task periodically (daily at midnight).
5. 📊 **Flower** displays task and worker status live.

---

## ✅ Component Roles Summary

| Component     | Purpose                                 |
| ------------- | --------------------------------------- |
| Flask         | Web app to trigger or view tasks        |
| Celery Worker | Runs background and scheduled tasks     |
| Celery Beat   | Sends periodic tasks into the queue     |
| RabbitMQ      | Message broker connecting everything    |
| Flower        | Web UI to monitor Celery task execution |

---
