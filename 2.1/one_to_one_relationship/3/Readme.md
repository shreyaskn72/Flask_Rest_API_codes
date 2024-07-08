Certainly! Below is a `README.md` script that explains the setup, usage, and structure of the Flask API for user management with the `user` and `profile` tables created manually in SQL:

---

# Flask API for User Management with SQLAlchemy and Manually Created Tables

This Flask application provides a simple API for user management, allowing CRUD operations on users and their associated profiles. SQLAlchemy is used for ORM to interact with the SQLite database, where the `user` and `profile` tables are manually created.

## Prerequisites

- Python 3.x
- Flask
- SQLAlchemy
- SQLite (or any other supported database system)

## Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create the SQLite database (`example.db`) and manually create the `user` and `profile` tables using the provided SQL script or your preferred database management tool.

   ```sql
   -- SQL script to create user and profile tables
   -- (Refer to previous message for SQL script)
   ```

   Replace `<repository-url>` and `<repository-directory>` with your actual repository URL and directory.

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

   - **POST /users**: Create a new user with username and email.

     ```bash
     curl -X POST \
       http://localhost:5000/users \
       -H 'Content-Type: application/json' \
       -d '{
         "username": "john_doe",
         "email": "john.doe@example.com"
       }'
     ```

   - **PUT /users/<user_id>/profile**: Update the profile of a user by ID.

     ```bash
     curl -X PUT \
       http://localhost:5000/users/<user_id>/profile \
       -H 'Content-Type: application/json' \
       -d '{
         "full_name": "Updated Full Name"
       }'
     ```

   - **PUT /users/<user_id>/fullname**: Update the full name of a user's profile, checking for uniqueness.

     ```bash
     curl -X PUT \
       http://localhost:5000/users/<user_id>/fullname \
       -H 'Content-Type: application/json' \
       -d '{
         "full_name": "Updated Full Name"
       }'
     ```

   - **DELETE /users/<user_id>**: Delete a user by ID.

     ```bash
     curl -X DELETE http://localhost:5000/users/<user_id>
     ```

3. Replace `<user_id>` with the actual user ID you want to interact with.

## Example Response

For `GET` requests, responses will be in JSON format:

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
### user table creation
```
-- Create the user table
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE
);
```
### profile table creation
```
-- Create the profile table
CREATE TABLE profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(120),
    user_id INTEGER UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

## Notes

- Ensure your database (`example.db`) is correctly set up with the `user` and `profile` tables before running the application.
- This example uses SQLite as the database. For production, consider using a more robust database like PostgreSQL, MySQL, etc.
- The API provides endpoints to manage users and their associated profiles efficiently, allowing dynamic updates and checks for existing data.
- Adjustments can be made based on specific application requirements or additional business logic needs.

---

This `README.md` provides clear instructions on setting up, running, and using the Flask API for user management with manually created `user` and `profile` tables. It includes examples of `curl` commands for each endpoint, ensuring ease of understanding and usage for developers interacting with the API. Adjustments can be made based on specific application requirements or additional functionality desired.