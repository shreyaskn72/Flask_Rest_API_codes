Here's a fully **merged** version of the project into **a single `app.py`** file, combining:

* Flask web server
* Celery worker
* Celery Beat periodic tasks
* RabbitMQ config
* Optional Flower monitor support (still run separately)

---

### ✅ Single File: `app.py`

```python
from flask import Flask
from celery import Celery
from celery.schedules import crontab
import requests

# -------------------------------
# 🔧 Configuration
# -------------------------------
class Config:
    CELERY_BROKER_URL = 'pyamqp://guest@localhost//'
    CELERY_RESULT_BACKEND = 'rpc://'

# -------------------------------
# ⚙️ Celery Setup
# -------------------------------
def make_celery(app_name=__name__):
    celery = Celery(
        app_name,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND
    )
    celery.conf.timezone = 'UTC'
    return celery

celery = make_celery()

# -------------------------------
# 🧠 Celery Task
# -------------------------------
@celery.task
def call_microservice():
    print("Calling microservice...")
    try:
        response = requests.get("https://httpbin.org/get")
        print("Microservice responded with:", response.status_code)
        return response.status_code
    except Exception as e:
        print("Error:", str(e))
        return str(e)

# -------------------------------
# ⏰ Celery Beat Schedule
# -------------------------------
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Runs daily at midnight UTC
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        call_microservice.s(),
        name='Daily microservice call'
    )

# -------------------------------
# 🌐 Flask App
# -------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Flask + Celery + RabbitMQ is running!"

@app.route('/trigger')
def trigger_task():
    call_microservice.delay()
    return "🚀 Task triggered!"

# -------------------------------
# 📌 Entry Point
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
```

---

### 🧪 How to Run Everything

You'll still need to run different components in separate terminal sessions (no way around it for Celery workers and Beat):

---

#### 1. Install Dependencies

```bash
pip install flask celery requests flower
```

---

#### 2. Run Flask App

```bash
export FLASK_APP=app.py  # Windows: set FLASK_APP=app.py
flask run
```

---

#### 3. Run Celery Worker

```bash
celery -A app.celery worker --loglevel=info
```

---

#### 4. Run Celery Beat (for scheduled tasks)

```bash
celery -A app.celery beat --loglevel=info
```

---

#### 5. (Optional) Run Flower to Monitor

```bash
celery -A app.celery flower --port=5555
```

Open your browser at [http://localhost:5555](http://localhost:5555)

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
