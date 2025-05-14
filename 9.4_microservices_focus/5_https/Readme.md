To secure your **Dockerized Flask application with HTTPS using Let's Encrypt and Nginx**, follow this comprehensive guide. This setup ensures encrypted traffic, enhances security, and is suitable for production environments.

---

## 🔧 Prerequisites

* **Domain Name**: Ensure you have a registered domain (e.g., `yourdomain.com`).
* **Docker & Docker Compose**: Installed on your machine.
* **Public Access**: Your server must be publicly accessible on ports 80 and 443.
* **Email Address**: For Let's Encrypt registration.

---

## 🧱 Updated Project Structure

```
flask_gunicorn_nginx/
├── app/
│   ├── app.py
│   ├── models.py
│   └── __init__.py
├── config.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── nginx/
│   ├── nginx.conf
│   └── ssl-renew.sh
└── certbot/
    └── Dockerfile
```

---

## 🛠️ 1. Nginx Configuration (`nginx/nginx.conf`)

Configure Nginx to handle HTTPS traffic and proxy requests to Gunicorn:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

*Replace `yourdomain.com` with your actual domain.*

---

## 🐳 2. Docker Compose Configuration (`docker-compose.yml`)

Set up services for Flask, Nginx, and Certbot:

```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: flask_app
    volumes:
      - .:/app
    expose:
      - 8000
    depends_on:
      - nginx

  nginx:
    image: nginx:alpine
    container_name: nginx_proxy
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/certbot:/var/www/certbot
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web

  certbot:
    image: certbot/certbot
    container_name: certbot
    volumes:
      - ./nginx/certbot:/var/www/certbot
      - ./nginx/certbot/conf:/etc/letsencrypt
      - ./nginx/certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

---

## 📦 3. Certbot Dockerfile (`certbot/Dockerfile`)

Create a custom Certbot image to handle SSL certificate generation:

```dockerfile
FROM certbot/certbot:v1.22.0

RUN apk add --no-cache bash
```

---

## 🛠️ 4. SSL Certificate Generation

Before starting the services, generate SSL certificates:

```bash
docker-compose run --rm --entrypoint "certbot certonly --webroot --webroot-path=/var/www/certbot --email your_email@example.com --agree-tos --no-eff-email -d yourdomain.com" certbot
```

*Replace `your_email@example.com` and `yourdomain.com` with your actual email and domain.*

---

## 🔄 5. Automate SSL Certificate Renewal

Create a script to renew certificates and reload Nginx:

```bash
#!/bin/bash
certbot renew
docker-compose exec nginx nginx -s reload
```

Save this as `nginx/ssl-renew.sh` and make it executable:

```bash
chmod +x nginx/ssl-renew.sh
```

Add a cron job to run the renewal script periodically:

```bash
crontab -e
```

Add the following line to the crontab:

```bash
0 3 * * * /path/to/your/project/nginx/ssl-renew.sh
```

---

## 🚀 6. Build and Run the Application

Build and start the services:

```bash
docker-compose up --build
```

Access your application at:

```
https://yourdomain.com/items
```

---

## ✅ Summary

| Component | Role                                        |
| --------- | ------------------------------------------- |
| Flask     | Handles API logic                           |
| Gunicorn  | WSGI server running Flask                   |
| Nginx     | Reverse proxy with SSL termination          |
| Certbot   | Manages SSL certificates from Let's Encrypt |
| Docker    | Containerizes the entire application        |

This setup provides a secure, scalable, and production-ready environment for your Flask application.

---