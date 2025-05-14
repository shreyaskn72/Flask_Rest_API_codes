Refer Readme.md if you dont need docker setup.
Below is a **complete Dockerized version** of the same **Flask + Celery + Celery Beat + RabbitMQ + Flower** project. It is structured for **clarity, learning**, and **easy development**.

---

# 🐳 Flask + Celery + RabbitMQ + Flower — Dockerized

---

## 📁 Folder Structure

```
flask_celery_docker/
│
├── app/                   
│   ├── __init__.py
│   ├── app.py            # Flask app
│   ├── tasks.py          # Celery tasks
│   └── beat_schedule.py  # Optional periodic tasks
│
├── celery_app/           
│   └── celery_config.py  # Celery factory + config
│
├── Dockerfile            # Flask + Celery image
├── docker-compose.yml    # Multi-service Docker setup
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 📦 1. `requirements.txt`

```txt
Flask==2.2.2
Celery==5.2.7
requests==2.28.1
flower==1.2.0
```

---

## ⚙️ 2. `celery_app/celery_config.py`

```python
from celery import Celery

def make_celery():
    celery = Celery(
        'flask_celery_project',
        broker='amqp://guest:guest@rabbitmq:5672//',
        backend='rpc://',
        include=['app.tasks']
    )
    celery.conf.timezone = 'UTC'
    return celery

celery = make_celery()
```

---

## 🔧 3. `app/__init__.py`

```python
from flask import Flask

def create_app():
    app = Flask(__name__)

    from .app import main_bp
    app.register_blueprint(main_bp)

    return app
```

---

## 🌐 4. `app/app.py` (Flask routes)

```python
from flask import Blueprint
from .tasks import call_microservice

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return "Flask + Celery + RabbitMQ (Dockerized)"

@main_bp.route('/trigger')
def trigger():
    call_microservice.delay()
    return "Task triggered!"
```

---

## ⚙️ 5. `app/tasks.py`

```python
from celery_app.celery_config import celery
import requests

@celery.task
def call_microservice():
    print("Calling microservice...")
    response = requests.get("https://httpbin.org/get")
    print("Response status:", response.status_code)
    return response.status_code
```

---

## ⏰ 6. `app/beat_schedule.py`

```python
from celery.schedules import crontab
from celery_app.celery_config import celery
from .tasks import call_microservice

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/1'),
        call_microservice.s(),
        name='call every minute'
    )
```

---

## 🐳 7. `Dockerfile`

```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["flask", "--app", "app", "run", "--host=0.0.0.0"]
```

---

## 🐳 8. `docker-compose.yml`

```yaml
version: '3.8'

services:
  web:
    build: .
    volumes:
      - .:/app
    ports:
      - "5000:5000"
    depends_on:
      - rabbitmq
    environment:
      - FLASK_ENV=development
    command: flask --app app run --host=0.0.0.0 --port=5000

  celery_worker:
    build: .
    command: celery -A celery_app.celery_config.celery worker --loglevel=info
    depends_on:
      - rabbitmq

  celery_beat:
    build: .
    command: celery -A celery_app.celery_config.celery beat --loglevel=info
    depends_on:
      - rabbitmq

  flower:
    build: .
    command: celery -A celery_app.celery_config.celery flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - rabbitmq

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
```

---

## 🚀 Run the Project

### 1. Build and run all services:

```bash
docker-compose up --build
```

### 2. Access the services:

* 🧪 Flask API: [http://localhost:5000](http://localhost:5000)

  * Trigger task: [http://localhost:5000/trigger](http://localhost:5000/trigger)

* 📬 Flower Dashboard: [http://localhost:5555](http://localhost:5555)

* 🐰 RabbitMQ UI: [http://localhost:15672](http://localhost:15672)
  (Login: `guest` / `guest`)

---

## 🔁 Full Flow

1. User hits `/trigger` → task sent to RabbitMQ.
2. Celery Worker picks it up and runs `call_microservice()`.
3. Celery Beat (optional) triggers the task every minute.
4. Flower displays live task/worker status.
5. RabbitMQ routes and queues tasks.

---

## ✅ Component Summary

| Service         | Role                                   |
| --------------- | -------------------------------------- |
| `web`           | Flask web server                       |
| `celery_worker` | Executes background tasks              |
| `celery_beat`   | Triggers scheduled tasks               |
| `rabbitmq`      | Task queue (broker)                    |
| `flower`        | Web UI to monitor Celery workers/tasks |

---

