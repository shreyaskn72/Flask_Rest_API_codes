
---

## ✅ 1. **Use `ps` to Find Gunicorn Processes**

Run this in your WSL terminal:

```bash
ps aux | grep gunicorn
```

Example output:

```
user      12345  0.1  2.3 123456 23456 ? S    13:00   0:00 gunicorn crud:app --bind 0.0.0.0:8000 --workers 2
```

This shows active Gunicorn processes. You’ll see:

* The command
* PID
* Which app is running
* How many workers

🧠 To **filter out the grep process** itself:

```bash
ps aux | grep '[g]unicorn'
```

---

## ✅ 2. **Use `lsof` to See What’s Listening on Port 8000**

```bash
sudo lsof -i :8000
```

This shows which process is using port `8000` (or any port you set for Gunicorn).

Example output:

```
gunicorn  12345 user   5u  IPv4 1234567      0t0  TCP *:8000 (LISTEN)
```

---

## ✅ 3. **Use `pgrep` to Get PIDs of Gunicorn**

```bash
pgrep -af gunicorn
```

Shows process ID **and full command**:

```
12345 gunicorn crud:app --bind 0.0.0.0:8000 --workers 2
```

---

## ✅ 4. **Use `systemctl` or `supervisorctl` (if you’ve daemonized Gunicorn)**

If you set up Gunicorn as a **systemd** service (rare in WSL), you’d use:

```bash
systemctl status gunicorn
```

Or if using **Supervisor**:

```bash
supervisorctl status
```

Let me know if you’d like help configuring Gunicorn as a persistent background service.

---

## ✅ 5. **Custom Alias (Optional)**

To quickly check Gunicorn processes each time you log in, add this to your WSL user’s `.bashrc` or `.zshrc`:

```bash
alias gstatus="ps aux | grep '[g]unicorn'"
```

Then just run:

```bash
gstatus
```

---

