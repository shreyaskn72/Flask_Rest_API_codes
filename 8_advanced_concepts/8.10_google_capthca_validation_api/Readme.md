# Google reCAPTCHA Validation API

This is a simple Python Flask API to validate Google reCAPTCHA codes. It provides an endpoint where you can send a reCAPTCHA token for validation.

## Setup

1. Clone the repository:

    ```bash
    git clone <repository-url>
    ```

2. Install the required dependencies. You can do this via pip:

    ```bash
    pip install -r requirements.txt
    ```

3. Obtain your reCAPTCHA secret key from the [Google reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin). Replace `'YOUR_SECRET_KEY_HERE'` in the code with your actual secret key.

## Usage

1. Run the Flask application:

    ```bash
    python app.py
    ```

2. Send a POST request to the `/validate-recaptcha` endpoint with a JSON payload containing the reCAPTCHA token:

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"token": "YOUR_RECAPTCHA_TOKEN"}' http://localhost:5000/validate-recaptcha
    ```

    Replace `YOUR_RECAPTCHA_TOKEN` with the actual reCAPTCHA token you want to validate.

3. You will receive a JSON response indicating whether the reCAPTCHA validation was successful or not.

## API Endpoint

- **POST /validate-recaptcha**: Validates a reCAPTCHA token provided in the request body. Returns a JSON response with the validation result.

    Request Body:
    ```json
    {
        "token": "YOUR_RECAPTCHA_TOKEN"
    }
    ```

    Response:
    ```json
    {
        "success": true,
        "message": "reCAPTCHA validation successful"
    }
    ```

    If the validation fails:
    ```json
    {
        "success": false,
        "message": "reCAPTCHA validation failed"
    }
    ```

## Dependencies

- Flask
- requests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
