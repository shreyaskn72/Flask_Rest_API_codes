#!/bin/bash

echo "🛑 Stopping Flask, Celery Worker, and Celery Beat..."

pkill -f "flask run"
pkill -f "celery -A app.celery worker"
pkill -f "celery -A app.celery beat"

echo "✅ All services stopped."
