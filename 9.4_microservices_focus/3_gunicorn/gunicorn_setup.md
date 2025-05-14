To run your **Flask CRUD API with SQLite** in **Gunicorn**, follow these steps:

---

## ✅ 1. Ensure Your Flask App Has an `app` Object

If you're using the single-file version (like `app.py`), Gunicorn looks for the Flask app variable called `app`. You already have this:

```python
app = Flask(__name__)
```

That means you're ready to run:

---

## ✅ 2. Install Gunicorn

In your virtual environment:

```bash
pip install gunicorn
```

Add to `requirements.txt`:

```
gunicorn==21.2.0
```

---

## ✅ 3. Run the Flask App with Gunicorn

Use the following command:

```bash
gunicorn app:app --bind 0.0.0.0:8000 --workers 2
```

### Breakdown:

* `app:app` → `filename:FlaskAppObject`

  * First `app` is the file name: `app.py`
  * Second `app` is the Flask instance inside it (`app = Flask(__name__)`)
* `--bind 0.0.0.0:8000` → Listen on port 8000 (or any other)
* `--workers 2` → Use 2 worker processes (adjust based on CPU)

---

## ✅ 4. Test It

Visit:

```bash
http://localhost:8000/items
```

Use `curl` or Postman to test endpoints as usual.

---

## ✅ Optional: Production Tips

| Tip                              | Command / Setting                  |
| -------------------------------- | ---------------------------------- |
| Daemonize                        | `--daemon`                         |
| Log to file                      | `--access-logfile logs/access.log` |
| Error log                        | `--error-logfile logs/error.log`   |
| Restart on code change (for dev) | `--reload`                         |

Example:

```bash
gunicorn app:app --bind 0.0.0.0:8000 --workers 2 --reload
```

---

## ✅ Bonus: Make a Bash Script

### `run_gunicorn.sh` (optional helper)

```bash
#!/bin/bash
gunicorn app:app --bind 0.0.0.0:8000 --workers 2
```

Make it executable:

```bash
chmod +x run_gunicorn.sh
./run_gunicorn.sh
```

---
