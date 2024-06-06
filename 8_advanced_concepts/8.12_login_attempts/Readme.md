# Flask API for User Registration, Login, and Account Lockout


This Flask API provides endpoints for user registration, login, and account lockout mechanism after multiple failed login attempts.


## API Endpoints
### 1. User Registration


- **Endpoint:** `/register`
- **Method:** `POST`
- **Request Body:**
```json
 {"email": "user@example.com", 
  "password": "your_password"}
```

- **Response:** 
  - `201 Created` on successful registration
  - `400 Bad Request` if username already exists

### 2. User Login
- **Endpoint:** `/login`
- **Method:** `POST`
- **Request Body:**
  ```json
   {"email": "user@example.com", "password": "your_password"}
  ```
  
- **Response:** 
    - `200 OK` on successful login
   - `401 Unauthorized` if incorrect password
    - `403 Forbidden` if account is locked out or permanently locked

### 3. API Endpoint for User Data
- Fetch User by User ID
- **Endpoint:**  `/user/<user_id>`
- **Method:**  `GET`
- **Response:** 
 ```json
{
    "id": 1,
    "email": "user@example.com",
    "locked": false,
    "login_attempts": [
        {"id": 1, "attempts": 3, "lockout_time": "2024-06-15 15:30:00"},
        {"id": 2, "attempts": 1, "lockout_time": null}
    ]
}

```

### 4. Unlock User Account
- **Endpoint:**  `/user/<user_id>`
- **Method:**  `PUT`
- **Response:** 
   - `200 OK` on successful unlock
   - `404 Not Found` if user with specified id not found
  

## Account Lockout
- After 5 failed login attempts, the account is locked out for 30 minutes.

- If the account fails to login again after the 30-minute lockout period, it is permanently locked.

## Curl Examples

### Register User

```bash
curl -X POST -H "Content-Type: application/json" -d '{"email": "user@example.com", "password": "your_password"}' http://localhost:5000/register

```


### Login User
```bash
curl -X POST -H "Content-Type: application/json" -d '{"email": "user@example.com", "password": "your_password"}' http://localhost:5000/login
```

### Fetch User Data
```bash
curl -X GET http://localhost:5000/user/1
```

Replace 1 with the desired user id you want to fetch.

### Unlock User Account
```bash
curl -X PUT http://localhost:5000/unlock/1
```
Replace 1 with the user id of the account you want to unlock.