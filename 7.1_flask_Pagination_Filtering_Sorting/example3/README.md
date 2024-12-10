# Flask Bookstore API

This Flask application provides a simple API for managing books in a bookstore. It allows users to perform CRUD operations (Create, Read, Update, Delete) on books stored in a SQLite database.

## Features

- **Get Books**: Retrieve a list of books with pagination and optional filtering by title, author, and genre.
- **Add Book**: Add a new book to the bookstore.
- **Error Handling**: Comprehensive error handling for database errors, missing fields, and other exceptions.
- **Logging**: Logging of errors and other events to a file (`app.log`).
- **Metrics**: Prometheus metrics for monitoring performance and request statistics.


The application will run on `http://localhost:5000` by default.

## Endpoints

### Get Books

- **URL**: `/books`
- **Method**: `GET`
- **Query Parameters**:
- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Number of books per page (default: 10)
- `title` (optional): Filter books by title (case-insensitive, partial match)
- `author` (optional): Filter books by author (case-insensitive, partial match)
- `genre` (optional): Filter books by genre (case-insensitive, partial match)
- **Response**:
- `200 OK`: Returns a list of books matching the query parameters.




The application will run on `http://localhost:5000` by default.

## Endpoints

### Get Books

- **URL**: `/books`
- **Method**: `GET`
- **Query Parameters**:
- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Number of books per page (default: 10)
- `title` (optional): Filter books by title (case-insensitive, partial match)
- `author` (optional): Filter books by author (case-insensitive, partial match)
- `genre` (optional): Filter books by genre (case-insensitive, partial match)
- **Response**:
- `200 OK`: Returns a list of books matching the query parameters.

### Add Book

- **URL**: `/books`
- **Method**: `POST`
- **Request Body**: JSON object containing book details (`title`, `author`, `genre`)
- **Response**:
- `201 Created`: Returns the details of the newly added book.
- `400 Bad Request`: If the request body is missing required fields.


#### Example CURL Request for Get Books

```bash
curl -X GET 'http://localhost:5000/books?page=1&page_size=10&title=&author=&genre=' \
-H 'Content-Type: application/json'

```

#### Example CURL Request for Add Book
```bash
curl -X POST 'http://localhost:5000/books' \
-H 'Content-Type: application/json' \
-d '{
    "title": "New Book",
    "author": "John Doe",
    "genre": "Fiction"
}'
```


## Error Handling

- `400 Bad Request`: Missing required fields or invalid input data.
- `500 Internal Server Error`: Database errors or other unexpected exceptions.

## Logging

- Errors and other events are logged to a file named `app.log`.

## Metrics

- Prometheus metrics are available at the `/metrics` endpoint for monitoring performance and request statistics.

## Contributors

- [SHREYAS K N](https://github.com/shreyaskn72)
