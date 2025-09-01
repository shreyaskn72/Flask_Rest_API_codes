### install gunicorn
```bash
pip3.12 install gunicorn
```

### install eventlet
```bash
pip3.12 install eventlet
```

### check python interpreter
```bash
which python3.12
```

output: /usr/bin/python3.12

### check for existing gunicorns
```bash
ps aux | grep gunicorn
```
### kill all existing gunicorn process
```bash
pkill gunicorn
```

### confirm no gunicorn is running using
```bash
pgrep -fl gunicorn
```

if nothing returns its all good


### Create folders Before Running Gunicorn:

Ensure the `logs/` directory exists:

```bash
mkdir -p logs
```
```bash
chmod u+w logs
```


```bash
mkdir -p gunicorn_pid
```
```
chmod 755 gunicorn_pid
```

### check the number of cpu cores
```bash
nproc
```
```
lscpu
```



## Command to capture logs without eventlet (max 9 wokers for 4 cores (2*n + 1))
```bash
nohup /usr/bin/python3.12 -m gunicorn app:app \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --log-level debug \
  --pid gunicorn_pid/gunicorn.pid \
  >> logs/gunicorn.log 2>&1 &
```


## Final Command (with `/usr/bin/python3.12` and eventlet)  (max 4 workers for 4 cores )



```bash
nohup /usr/bin/python3.12 -m gunicorn app:app \
  --bind 0.0.0.0:8000 \
  --worker-class eventlet \
  --workers 4 \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --log-level debug \
  --pid gunicorn_pid/gunicorn.pid \
  >> logs/gunicorn.log 2>&1 &
```
---

### stopping the above gunicorn
```
pkill -f "gunicorn app:app"
```




### How to Use shell scripting

`server.sh`


```bash
#!/bin/bash

APP_MODULE="app:app"
PID_FILE="gunicorn_pid/gunicorn.pid"
LOG_FILE="logs/gunicorn.log"
PYTHON_BIN="/usr/bin/python3.12"
WORKERS=2

start_server() {
    echo "Starting Gunicorn server..."
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
    echo "Gunicorn started. Logs: $LOG_FILE"
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
1. **Save the script** as `server.sh` in the directory. Navigate to it.
2. **Make it executable**:

   ```bash
   chmod +x server.sh
   ```
   ***push the permission change as well to git***
   ```bash
   git add server.sh
   git commit -m "Make server.sh executable"
   git push origin your-branch
   ```
   

3. **Run it**:

   * To **start** the server:

     ```bash
     ./server.sh start
     ```
   * To **stop** the server:

     ```bash
     ./server.sh stop
     ```
   * To **restart**:

     ```bash
     ./server.sh restart
     ```

---