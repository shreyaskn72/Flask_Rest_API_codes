# Flask API with SQLAlchemy - Filtering, Sorting, Pagination

This is a Flask API that provides endpoints for retrieving books from a database with support for filtering, sorting, and pagination. SQLAlchemy is used for interacting with the database.


Run the Flask application:

```bash
python example2.py
```

The Flask application should now be running on `http://localhost:5000`.

## Usage

### Endpoints

#### GET /books

Retrieves a list of books with support for filtering, sorting, and pagination.

#### Query Parameters

- `page`: Page number (default: 1)
- `page_size`: Number of books per page (default: 10)
- `title`: Filter books by title (case-insensitive)
- `author`: Filter books by author (case-insensitive)
- `genre`: Filter books by genre (case-insensitive)
- `sort_by`: Sort books by a field (e.g., `title`, `author`, `genre`)

### Example CURL Request

```bash
curl -X GET 'http://localhost:5000/books?page=1&page_size=5&title=Book&sort_by=title' \
-H 'Content-Type: application/json'
