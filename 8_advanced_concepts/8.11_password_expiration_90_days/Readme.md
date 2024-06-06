# Flask API for User Registration and Password Management

This Flask API provides endpoints for registering users with username and password, changing passwords, and validating if a password has expired.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your_username/flask-password-api.git
   ```

2. Navigate to the project directory:

   ```bash
   cd flask-password-api
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask app:

   ```bash
   python app.py
   ```

## API Endpoints

### 1. User Registration

- **Endpoint:** `/register`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
      "username": "your_username",
      "password": "your_password"
  }
  ```
- **Response:** 
  - `201 Created` on successful registration
  - `400 Bad Request` if username already exists

### 2. Change Password

- **Endpoint:** `/change_password`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
      "username": "your_username",
      "old_password": "your_old_password",
      "new_password": "your_new_password"
  }
  ```
- **Response:** 
  - `200 OK` on successful password change
  - `404 Not Found` if user not found
  - `400 Bad Request` if old password is incorrect

### 3. Validate Password Expiry

- **Endpoint:** `/password_expired`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
      "username": "your_username"
  }
  ```
- **Response:** 
  - `200 OK` with message "Password has expired" if password has expired
  - `200 OK` with message "Password is still valid" if password is still valid
  - `404 Not Found` if user not found

## Curl Examples

### Register User
```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "your_username", "password": "your_password"}' http://localhost:5000/register
```

### Change Password
```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "your_username", "old_password": "your_old_password", "new_password": "your_new_password"}' http://localhost:5000/change_password
```

### Validate Password Expiry
```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "your_username"}' http://localhost:5000/password_expired
```
