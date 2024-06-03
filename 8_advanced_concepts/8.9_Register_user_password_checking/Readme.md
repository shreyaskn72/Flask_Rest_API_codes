# User Registration Flask API

This Flask API provides endpoints to register users with password validation.

## Features

- Allows users to register with a username and password.
- Validates the password according to specified criteria:
  - At least one uppercase letter.
  - At least one lowercase letter.
  - At least one digit.
  - At least one special character.
  - Minimum length of 9 characters and maximum length of 20 characters.
  - Does not contain the user's first name, last name, or middle name.

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

## Usage

1. Run the Flask application:

    ```bash
    python app.py
    ```

2. Send a POST request to the `/register` endpoint with JSON data containing `username` and `password` fields. Optionally, you can include `first_name`, `last_name`, and `middle_name` fields.

    Example:

    ```bash
    curl -X POST http://localhost:5000/register -H "Content-Type: application/json" -d '{"username": "example_user", "password": "StrongPassword123!", "first_name": "John", "last_name": "Doe"}'
    ```

3. The API will validate the password and return a success message if the registration is successful, or an error message if the validation fails.

## Endpoints

- **POST /register**: Register a new user.

  Request Body:

  ```json
  {
      "username": "string",
      "password": "string",
      "first_name": "string",
      "last_name": "string",
      "middle_name": "string"
  }
  ```
  
## Response:

- Success: Status 200
```json
{
    "message": "User <username> registered successfully."
}
```
- Error: Status 400
```json
{
    "error": "Error message"
}
```



