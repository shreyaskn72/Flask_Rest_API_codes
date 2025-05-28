running **Gunicorn behind Nginx** is the standard production setup for serving Flask apps. Nginx acts as a **reverse proxy**, handling:

* Static files
* HTTPS (TLS termination)
* Load balancing (if needed)
* Buffering and performance optimization

---

## ✅ Architecture Overview

```
Client (browser/Postman) → Nginx (port 80/443) → Gunicorn (port 8000) → Flask App
```

---

## 🔧 Step-by-Step: Set Up Nginx + Gunicorn in WSL

### ⚙️ Assumptions:

* Flask app: `crud.py`, app object: `app`
* Gunicorn running on `localhost:8000`
* Project path: `/home/youruser/crud-app`
* You want Nginx to serve it on port 80 (http)

---

### 🔹 1. Install Nginx

In WSL:

```bash
sudo apt update
sudo apt install nginx
```

Start it:

```bash
sudo service nginx start
```

---

### 🔹 2. Run Gunicorn on localhost

Make sure Gunicorn **only listens on 127.0.0.1** (not exposed to public):

```bash
gunicorn --workers 2 --bind 127.0.0.1:8000 crud:app
```

---

### 🔹 3. Configure Nginx to Proxy to Gunicorn

Create a config file:

```bash
sudo nano /etc/nginx/sites-available/flaskapp
```

Paste this basic config:

```nginx
server {
    listen 80;
    server_name localhost;

    access_log /var/log/nginx/flaskapp_access.log;
    error_log  /var/log/nginx/flaskapp_error.log;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Save and link it:

```bash
sudo ln -s /etc/nginx/sites-available/flaskapp /etc/nginx/sites-enabled/
```

Test config:

```bash
sudo nginx -t
```

Reload Nginx:

```bash
sudo systemctl reload nginx
```

---

### 🔹 4. Test Your Setup

From Windows browser or Postman:

```
http://localhost/items
```

✅ This should hit:

* Nginx on port 80
* Forward to Gunicorn on 127.0.0.1:8000
* Gunicorn runs your Flask API

---

### 🛡️ (Optional) 5. Add HTTPS with Let's Encrypt (via `certbot`)

Only possible if you're exposing your WSL instance to the internet (e.g., via port forwarding or tunneling). Ask if you want guidance.

---

## 🧼 Bonus: Serve Static Files via Nginx (if needed)

To serve static content directly from Nginx (faster than Flask/Gunicorn):

Add inside your Nginx `server {}` block:

```nginx
location /static/ {
    alias /home/youruser/crud-app/static/;
}
```

---

## ✅ Summary of Commands

```bash
# Install nginx
sudo apt install nginx

# Start Gunicorn (internally)
gunicorn --bind 127.0.0.1:8000 crud:app

# Configure nginx to proxy
sudo nano /etc/nginx/sites-available/flaskapp
sudo ln -s /etc/nginx/sites-available/flaskapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

Next steps:

* Auto-restart on reboot (systemd/supervisor)
* TLS certs for HTTPS
* Domain name routing (e.g., `api.example.com`)
* Load balancing across multiple Gunicorns


