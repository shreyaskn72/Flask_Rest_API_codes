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




For **production**, you want a shell script that **starts all necessary services cleanly**, manages **logging**, and ensures that processes are **restarted or supervised** if needed.

However, in **production**, using a **process manager** like `systemd`, **supervisord**, or running your stack in **Docker**/**Kubernetes** is **more robust** than a plain shell script. But if you're going with a shell script as a first step, here's how to do it properly.

---

## ✅ Production-Grade Shell Script Example (`start_services.sh`)

```bash
#!/bin/bash

# -----------------------------
# 🛠 Configuration
# -----------------------------
APP_MODULE="app"   # your app filename without .py
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

# -----------------------------
# 🌐 Start Flask App (using flask run)
# -----------------------------
echo "✅ Starting Flask app with 'flask run'..."
export FLASK_APP=$APP_MODULE.py
nohup flask run --host=0.0.0.0 > "$LOG_DIR/flask.log" 2>&1 &

# -----------------------------
# ⚙️ Start Celery Worker
# -----------------------------
echo "🚀 Starting Celery worker..."
nohup celery -A $APP_MODULE.celery worker --loglevel=info > "$LOG_DIR/celery_worker.log" 2>&1 &

# -----------------------------
# ⏰ Start Celery Beat
# -----------------------------
echo "⏰ Starting Celery beat..."
nohup celery -A $APP_MODULE.celery beat --loglevel=info > "$LOG_DIR/celery_beat.log" 2>&1 &

echo "🎉 All services started. Logs are in $LOG_DIR"

```

---

## 🧠 Key Features

* ✅ `nohup` runs each process **in the background** and **detaches** it from the terminal.
* ✅ `2>&1` redirects both `stdout` and `stderr` to log files.
* ✅ Logs are stored in a folder (`./logs/`).

---

## 🔄 Optional: Stop Script (`stop_services.sh`)

```bash
#!/bin/bash

echo "🛑 Stopping Flask, Celery Worker, and Celery Beat..."

pkill -f "flask run"
pkill -f "celery -A app.celery worker"
pkill -f "celery -A app.celery beat"

echo "✅ All services stopped."

```

> This is a **simple but effective** way to stop all related processes.

---

## ✅ Permissions

Make both scripts executable:

```bash
chmod +x start_services.sh stop_services.sh
```

Then run:

```bash
./start_services.sh
```

---

## 🛡️ For Real Production: Use One of These

For **resilience, automatic restarts, logging**, etc., consider:

| Option           | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| `systemd`        | Native Linux process manager                                 |
| `supervisord`    | Lightweight process supervisor                               |
| `Docker`         | Isolated containers for each service                         |
| `docker-compose` | Manage multi-container setups                                |
| `PM2`            | Good for process management (mainly for Node.js, but usable) |

---

