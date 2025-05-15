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