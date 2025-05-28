Let's **Dockerize your Flask + Gunicorn app** (without Nginx for now) in a clean and minimal way.

---

## ✅ Goal

Create a Docker container that:

* Runs your Flask CRUD app (`crud.py`)
* Uses Gunicorn as the WSGI server
* Exposes it on port `8000`

---

## 🧱 Project Structure

Here’s what your folder should look like:

```
crud-app/
│
├── crud.py
├── requirements.txt
└── Dockerfile
```

---

## 📄 1. `crud.py` (your existing Flask app)

You already have this — make sure your Flask app is named `app`:

```python
app = Flask(__name__)
```

---

## 📄 2. `requirements.txt`

List your dependencies:

```txt
Flask==2.2.5
gunicorn==21.2.0
flask_sqlalchemy==3.1.1
```

Adjust versions as needed.

---

## 📄 3. `Dockerfile`

Create a file named `Dockerfile`:

```Dockerfile
# Use an official Python runtime
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 8000

# Run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "crud:app", "--workers", "2"]
```

---

## 🐳 4. Build & Run the Docker Container

### Build the Docker image:

```bash
docker build -t flask-crud .
```

### Run the container:

```bash
docker run -d -p 8000:8000 --name flask-crud-app flask-crud
```

✅ Now access your API at:

```
http://localhost:8000/items
```

---

## 🛑 5. To Stop or Clean Up

Stop:

```bash
docker stop flask-crud-app
```

Remove container:

```bash
docker rm flask-crud-app
```

Remove image:

```bash
docker rmi flask-crud
```

---

## ✅ Summary

| Task            | Command                                 |
| --------------- | --------------------------------------- |
| Build image     | `docker build -t flask-crud .`          |
| Run container   | `docker run -d -p 8000:8000 flask-crud` |
| View in browser | `http://localhost:8000/items`           |
| Stop container  | `docker stop flask-crud-app`            |

---

Next steps:

* Add a Docker volume for the SQLite DB
* Use `docker-compose`
* Layer in Nginx later


