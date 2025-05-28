Let’s walk through how to **stop existing Gunicorn processes** and how to set up **auto-restart on crash or reboot**.

---

## ✅ PART 1: Stop Existing Gunicorn Processes

You have a few options:

### 🔹 Option 1: Kill by Port (e.g. port 8000)

```bash
sudo fuser -k 8000/tcp
```

This kills whatever process is using port 8000 — including Gunicorn.

---

### 🔹 Option 2: Kill All Gunicorn Processes

```bash
pkill gunicorn
```

Or more precise:

```bash
pkill -f 'gunicorn crud:app'
```

### 🔹 Option 3: Manually kill by PID

List all Gunicorn processes:

```bash
ps aux | grep '[g]unicorn'
```

Then:

```bash
kill -9 <PID>
```

---

## ✅ PART 2: Auto-Restart Gunicorn on Crash or Reboot

Here are 2 solid ways to do this:

---

### 🔹 Option A: Using `systemd` (if supported in WSL)

WSL (especially WSL2) **can now support systemd** if you have it enabled.

#### ✅ Step-by-step:

1. **Create a Gunicorn service file**
   Create file:

   ```bash
   sudo nano /etc/systemd/system/gunicorn.service
   ```

2. **Paste this config** (modify as needed):

```ini
[Unit]
Description=Gunicorn for Flask CRUD API
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:8000 crud:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

3. **Enable and start the service**:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
```

4. **Check status:**

```bash
systemctl status gunicorn
```

✅ Now it:

* Restarts on crash
* Starts on boot (if `systemd` is active in WSL)

---

### 🔹 Option B: Using `supervisord` (alternative for WSL/cron environments)

If `systemd` isn't available in WSL, use **Supervisor**:

#### Install Supervisor:

```bash
sudo apt install supervisor
```

#### Add a config:

```bash
sudo nano /etc/supervisor/conf.d/gunicorn.conf
```

Paste this:

```ini
[program:gunicorn]
directory=/path/to/your/project
command=/path/to/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:8000 crud:app
autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn.err.log
stdout_logfile=/var/log/gunicorn.out.log
user=yourusername
```

Then run:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start gunicorn
```

Check status:

```bash
sudo supervisorctl status
```

---

## ✅ Summary

| Task                | Command / Tool                          |                 |
| ------------------- | --------------------------------------- | --------------- |
| Kill Gunicorn       | `pkill gunicorn` or `fuser -k 8000/tcp` |                 |
| See Gunicorn        | \`ps aux                                | grep gunicorn\` |
| Auto-restart (WSL2) | `systemd` (via service file)            |                 |
| Auto-restart (WSL1) | `supervisord`                           |                 |

---


