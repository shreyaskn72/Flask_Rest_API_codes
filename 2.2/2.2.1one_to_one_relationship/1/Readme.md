
# Flask API with CRUD Operations and One-to-One Relationship

This Flask application demonstrates a simple API that allows performing CRUD operations on users and their associated profiles. It uses Flask for the web framework and SQLAlchemy for ORM (Object-Relational Mapping) to interact with the SQLite database.

## Prerequisites

- Python 3.x
- Flask
- SQLAlchemy

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Setup

1. Ensure your database URI is correctly configured in `app.py`:

   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
   ```

   Replace `'sqlite:///example.db'` with your preferred database URI.

2. Initialize the database:

   ```bash
   python app.py
   ```

   This command will create the SQLite database (`example.db`) and set up the necessary tables defined in `app.py`.

## Usage

1. Start the Flask server:

   ```bash
   python app.py
   ```

2. Use `curl` commands or a tool like Postman to interact with the API endpoints:

   ### API Endpoints

   - **GET /users**: Retrieve all users.

     ```bash
     curl -X GET http://localhost:5000/users
     ```

   - **GET /users/<user_id>**: Retrieve a specific user by ID.

     ```bash
     curl -X GET http://localhost:5000/users/<user_id>
     ```

   - **POST /users**: Create a new user and their profile.

     ```bash
     curl -X POST \
       http://localhost:5000/users \
       -H 'Content-Type: application/json' \
       -d '{
         "username": "john_doe",
         "email": "john.doe@example.com",
         "full_name": "John Doe"
       }'
     ```

   - **PUT /users/<user_id>**: Update an existing user and their profile by ID.

     ```bash
     curl -X PUT \
       http://localhost:5000/users/<user_id> \
       -H 'Content-Type: application/json' \
       -d '{
         "username": "new_username",
         "email": "new.email@example.com",
         "full_name": "Updated Name"
       }'
     ```
     
   - **PUT /users/<user_id>/profile**: Update an existing user's profile by ID.

     ```bash
     curl -X PUT \
     http://localhost:5000/users/1/profile \
     -H 'Content-Type: application/json' \
     -d '{
     "full_name": "Updated Full Name"
     }'
     ```

   - **DELETE /users/<user_id>**: Delete a user by ID.

     ```bash
     curl -X DELETE http://localhost:5000/users/<user_id>
     ```

3. Adjust the base URL (`http://localhost:5000`) if your Flask server is running on a different host or port.

## Example Response

For GET requests, responses will be in JSON format:

```json
{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "profile": {
    "full_name": "John Doe"
  }
}
```

## Manual sql script
```
-- Create User table
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE
);

-- Create Profile table
CREATE TABLE profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(120) NOT NULL,
    user_id INTEGER UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```


## Notes

- Ensure your database URI (`app.config['SQLALCHEMY_DATABASE_URI']`) is correctly configured before running the application.
- This example uses SQLite as the database. For production, consider using a more robust database like PostgreSQL, MySQL, etc.
- Additional error handling and input validation may be necessary depending on your specific requirements.

---

This `README.md` provides a clear overview of how to set up, run, and use the Flask API for performing CRUD operations and managing a one-to-one relationship between users and their profiles. Adjustments can be made based on your specific application requirements and preferences.