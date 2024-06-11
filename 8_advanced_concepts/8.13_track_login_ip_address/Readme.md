# User Registration and Login API

This is a Flask API for user registration, login, and logging IP addresses along with timestamps.

## Requirements

- Python 3.x
- Flask
- Flask-SQLAlchemy




## Endpoints

### User Registration

POST /register


Registers a new user with a unique username and email.

Example:

```bash
curl -X POST http://localhost:5000/register -H "Content-Type: application/json" -d '{"username": "user1", "email": "user1@example.com", "password": "password"}'
```

User Login



POST /login


Logs in an existing user and logs their IP address along with a timestamp.

Example:

```bash
curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"username": "user1", "password": "password"}'
```

Get User Logs

GET /user_logs


Retrieves all user logs including user IDs, IP addresses, and timestamps.

Example:
```bash
curl http://localhost:5000/user_logs
```

# Retrieve User Logs API

This API endpoint allows you to retrieve all logs associated with a specific user.

## cURL Command

To fetch all logs (including ID, timestamp, and IP address) associated with a user with a specific user ID, use the following cURL command:

```bash
curl http://localhost:5000/user/<user_id>/logs
```

Replace <user_id> with the ID of the user you want to fetch logs for.

Example
To fetch all logs for a user with ID 1:
```bash
curl http://localhost:5000/user/1/logs
```

This will return a JSON response containing the user ID and a list of logs with ID, timestamp, and IP address.