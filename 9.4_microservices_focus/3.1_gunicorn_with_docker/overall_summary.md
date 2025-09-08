Here's a full end-to-end **Dockerized Flask CRUD API with MySQL**, managed inside the container by your **custom shell script** to control Gunicorn.

---

# 🚀 Full Project Setup

---

## 🧱 Project Structure

```
flask_crud_api/
│
├── app.py
├── requirements.txt
├── gunicorn_server.sh
├── Dockerfile
├── docker-compose.yml
├── .env
```

---

## 1️⃣ `app.py` (Flask + SQLAlchemy + MySQL)

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "author": self.author}

@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict()), 200

@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    new_book = Book(title=data['title'], author=data['author'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify(new_book.to_dict()), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    db.session.commit()
    return jsonify(book.to_dict()), 200

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"}), 200

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run()
```

---

## 2️⃣ `requirements.txt`

```txt
flask
flask_sqlalchemy
pymysql
gunicorn
eventlet
python-dotenv
```

---

## 3️⃣ `.env`

```env
MYSQL_USER=myuser
MYSQL_PASSWORD=mypassword
MYSQL_DATABASE=mydb
MYSQL_ROOT_PASSWORD=rootpass
MYSQL_HOST=mysql
MYSQL_PORT=3306
```

---

## 4️⃣ `gunicorn_server.sh` (Your shell script managing Gunicorn)

```bash
#!/bin/bash

APP_MODULE="app:app"
PID_FILE="gunicorn_pid/gunicorn.pid"
LOG_FILE="logs/gunicorn.log"
PYTHON_BIN="/usr/local/bin/python"  # Use python from container, check with `which python` inside container
WORKERS=2

start_server() {
    echo "Starting Gunicorn server..."

    mkdir -p "$(dirname "$PID_FILE")"
    mkdir -p "$(dirname "$LOG_FILE")"

    nohup $PYTHON_BIN -m gunicorn $APP_MODULE \
      --bind 0.0.0.0:8000 \
      --worker-class eventlet \
      --workers $WORKERS \
      --access-logfile - \
      --error-logfile - \
      --capture-output \
      --log-level debug \
      --pid $PID_FILE \
      >> $LOG_FILE 2>&1 &

    sleep 1
    echo "Gunicorn started. Logs: $LOG_FILE, PID file: $PID_FILE"
}

stop_server() {
    if [ -f "$PID_FILE" ]; then
        echo "Stopping Gunicorn using PID file..."
        kill -TERM $(cat $PID_FILE) && rm -f $PID_FILE
        echo "Gunicorn stopped."
    else
        echo "PID file not found. Trying pkill fallback..."
        pkill -f "gunicorn $APP_MODULE"
        echo "Fallback kill attempted."
    fi
}

case "$1" in
  start)
    start_server
    ;;
  stop)
    stop_server
    ;;
  restart)
    stop_server
    sleep 2
    start_server
    ;;
  *)
    echo "Usage: $0 {start|stop|restart}"
    exit 1
    ;;
esac
```

---

## 5️⃣ `Dockerfile`

```Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Create directories used by the script
RUN mkdir -p gunicorn_pid logs

# Make the shell script executable
RUN chmod +x ./gunicorn_server.sh

EXPOSE 8000

ENTRYPOINT ["./gunicorn_server.sh"]
CMD ["start"]
```

---

## 6️⃣ `docker-compose.yml`

```yaml
version: '3.8'

services:
  flask-api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - mysql
    volumes:
      - .:/app
    command: ["start"]

  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

---

# 🔥 How to run it:

### Build & start with docker-compose:

```bash
docker-compose up --build
```

* MySQL will start first (`depends_on` ensures startup order).
* Flask app container will start, run your shell script with `start` argument.
* Gunicorn will launch inside container with your shell script.
* Logs and PID files saved inside container under `logs/` and `gunicorn_pid/`.

---

### To interact with your app:

* Visit API: [http://localhost:8000/books](http://localhost:8000/books)
* Curl example:

```bash
curl -X POST http://localhost:8000/books \
    -H "Content-Type: application/json" \
    -d '{"title": "Clean Code", "author": "Robert C. Martin"}'
```

---

### To control Gunicorn inside the container:

```bash
# Restart
docker exec -it <flask-container-id> ./gunicorn_server.sh restart

# Stop
docker exec -it <flask-container-id> ./gunicorn_server.sh stop

# Start
docker exec -it <flask-container-id> ./gunicorn_server.sh start
```

---

# 📖 Explanation:

| Part               | Purpose/Details                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------- |
| **Flask app**      | `app.py` with SQLAlchemy connecting to MySQL using env vars.                                |
| **Shell script**   | Controls Gunicorn inside container with start/stop/restart using PID file and logs.         |
| **Dockerfile**     | Builds image, installs deps, copies code, makes shell script executable, exposes port 8000. |
| **Docker Compose** | Runs both MySQL and Flask app, passes env vars, sets container dependencies.                |
| **.env file**      | Stores database credentials and connection info, loaded by Flask via python-dotenv.         |
| **Volumes**        | Persist MySQL data on host machine.                                                         |

---

# 🧩 Optional Tips:

* Mount log and pid directories as volumes if you want logs outside container.
* Use `wait-for-it` script or similar to delay Flask start until MySQL is fully ready.
* Add healthchecks in docker-compose for production readiness.
* Use a process manager if you want multiple processes in container (not common for Flask).

---

