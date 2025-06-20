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
