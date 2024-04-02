# Flask API with Token-Based Authentication

This is a simple Flask API that provides token-based authentication using Flask-JWT-Extended. It includes endpoints for user authentication, token generation, and protected routes that require authentication.

## Curl Endpoints

1. Send a POST request to `/auth` endpoint with a JSON payload containing the username and password to authenticate and receive access and refresh tokens along with their expiry times:



```
curl -X POST -H "Content-Type: application/json" -d '{"username":"user1","password":"password1"}' http://localhost:5000/auth
```

2. Use the obtained access token to access protected endpoints:


```
curl -X GET -H "Authorization: Bearer <access_token>" http://localhost:5000/hello
```
3. If the access token expires, use the refresh token to obtain a new access token:


```
curl -X POST -H "Content-Type: application/json" -d '{"refresh_token":"<refresh_token>"}' http://localhost:5000/refresh
```

## Endpoints

- `/auth` (POST): Authenticates users and generates access and refresh tokens.
  - Request body: `{ "username": "<username>", "password": "<password>" }`
  - Response: `{ "access_token": "<access_token>", "access_token_expiry": "<expiry_time>", "refresh_token": "<refresh_token>", "refresh_token_expiry": "<expiry_time>" }`

- `/hello` (GET): Protected endpoint that requires authentication. Returns a "Hello, World!" message along with the current user's identity.
  - Requires a valid access token in the Authorization header.

- `/refresh` (POST): Endpoint to refresh the access token using the refresh token.
  - Request body: `{ "refresh_token": "<refresh_token>" }`
  - Response: `{ "access_token": "<new_access_token>", "access_token_expiry": "<new_expiry_time>" }`

## Configuration

- JWT_SECRET_KEY: Secret key used to encode JWT tokens.
- JWT_ACCESS_TOKEN_EXPIRES: Expiry time for access tokens.
- JWT_REFRESH_TOKEN_EXPIRES: Expiry time for refresh tokens.
