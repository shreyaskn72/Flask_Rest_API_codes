We'll use the following routes:
- **Create**: For adding new authors and books.
- **Read**: For fetching authors and books, with support for pagination, sorting, and filtering.
- **Update**: For modifying an existing author or book.
- **Delete**: For removing an author or book from the database.

We'll ensure that we use `db.session.query` for the database queries.

### Updated Code with CRUD Operations and pagination,filtering, searching, sorting qpi:

```python
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_, desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Author model
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    books = db.relationship('Book', backref='author', lazy=True)

    def __repr__(self):
        return f"<Author {self.name}>"

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    def __repr__(self):
        return f"<Book {self.title}>"

# Create the database
with app.app_context():
    db.create_all()

# Create Author API (Create Operation)
@app.route('/authors', methods=['POST'])
def create_author():
    data = request.get_json()
    author_name = data.get('name')
    
    # Create new author
    new_author = Author(name=author_name)
    db.session.add(new_author)
    db.session.commit()
    
    return jsonify({"message": "Author created successfully", "author_id": new_author.id}), 201

# Create Book API (Create Operation)
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    book_title = data.get('title')
    author_id = data.get('author_id')
    
    # Create new book
    new_book = Book(title=book_title, author_id=author_id)
    db.session.add(new_book)
    db.session.commit()
    
    return jsonify({"message": "Book created successfully", "book_id": new_book.id}), 201

# Read Authors and Books with Pagination, Sorting, and Filtering (Read Operation)
@app.route('/search', methods=['GET'])
def search():
    author_name = request.args.get('author_name', None)
    book_title = request.args.get('book_title', None)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    sort_by = request.args.get('sort_by', 'author_name')
    sort_order = request.args.get('sort_order', 'asc')

    query = db.session.query(Author, Book).join(Book, Author.id == Book.author_id)
    
    if author_name and book_title:
        query = query.filter(and_(
            Author.name.like(f'%{author_name}%'),
            Book.title.like(f'%{book_title}%')
        ))
    elif author_name:
        query = query.filter(Author.name.like(f'%{author_name}%'))
    elif book_title:
        query = query.filter(Book.title.like(f'%{book_title}%'))
    else:
        query = query.filter(or_(
            Author.name.like(f'%{author_name}%'),
            Book.title.like(f'%{book_title}%')
        ))

    if sort_by == 'book_title':
        if sort_order == 'asc':
            query = query.order_by(Book.title.asc())
        elif sort_order == 'desc':
            query = query.order_by(Book.title.desc())
    else:
        if sort_order == 'asc':
            query = query.order_by(Author.name.asc())
        elif sort_order == 'desc':
            query = query.order_by(Author.name.desc())

    paginated_results = query.paginate(page=page, per_page=per_page, error_out=False)

    result_list = []
    for author, book in paginated_results.items:
        result_list.append({
            'author_id': author.id,
            'author_name': author.name,
            'book_id': book.id,
            'book_title': book.title
        })

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': paginated_results.total,
        'total_pages': paginated_results.pages,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'items': result_list
    })

# Update Author API (Update Operation)
@app.route('/authors/<int:id>', methods=['PUT'])
def update_author(id):
    data = request.get_json()
    new_name = data.get('name')
    
    # Query the author to update
    author = db.session.query(Author).get(id)
    
    if not author:
        return jsonify({"message": "Author not found"}), 404
    
    # Update author name
    author.name = new_name
    db.session.commit()
    
    return jsonify({"message": "Author updated successfully", "author_id": author.id})

# Update Book API (Update Operation)
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.get_json()
    new_title = data.get('title')
    new_author_id = data.get('author_id')
    
    # Query the book to update
    book = db.session.query(Book).get(id)
    
    if not book:
        return jsonify({"message": "Book not found"}), 404
    
    # Update book title and author
    book.title = new_title
    book.author_id = new_author_id
    db.session.commit()
    
    return jsonify({"message": "Book updated successfully", "book_id": book.id})

# Delete Author API (Delete Operation)
@app.route('/authors/<int:id>', methods=['DELETE'])
def delete_author(id):
    # Query the author to delete
    author = db.session.query(Author).get(id)
    
    if not author:
        return jsonify({"message": "Author not found"}), 404
    
    # Delete author and associated books
    db.session.delete(author)
    db.session.commit()
    
    return jsonify({"message": "Author and associated books deleted successfully"})

# Delete Book API (Delete Operation)
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    # Query the book to delete
    book = db.session.query(Book).get(id)
    
    if not book:
        return jsonify({"message": "Book not found"}), 404
    
    # Delete book
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({"message": "Book deleted successfully"})

# Bulk Create Authors API
@app.route('/authors/bulk', methods=['POST'])
def bulk_create_authors():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"message": "Request body must be a list of authors"}), 400

    authors = []
    for author_data in data:
        author_name = author_data.get('name')
        if not author_name:
            return jsonify({"message": "Each author must have a 'name' field"}), 400
        new_author = Author(name=author_name)
        authors.append(new_author)

    db.session.bulk_save_objects(authors)
    db.session.commit()

    return jsonify({"message": f"{len(authors)} authors created successfully"}), 201

# Bulk Create Books API
@app.route('/books/bulk', methods=['POST'])
def bulk_create_books():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"message": "Request body must be a list of books"}), 400

    books = []
    for book_data in data:
        book_title = book_data.get('title')
        author_id = book_data.get('author_id')

        if not book_title or not author_id:
            return jsonify({"message": "Each book must have 'title' and 'author_id' fields"}), 400

        new_book = Book(title=book_title, author_id=author_id)
        books.append(new_book)

    db.session.bulk_save_objects(books)
    db.session.commit()

    return jsonify({"message": f"{len(books)} books created successfully"}), 201

# Bulk Delete Authors API
@app.route('/authors/bulk', methods=['DELETE'])
def bulk_delete_authors():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"message": "Request body must be a list of author IDs"}), 400

    deleted_count = 0
    for author_id in data:
        if not isinstance(author_id, int):
            return jsonify({"message": "Each author ID must be an integer"}), 400

        # Find the author by ID
        author = db.session.query(Author).get(author_id)
        
        if author:
            db.session.delete(author)
            deleted_count += 1
        else:
            return jsonify({"message": f"Author with ID {author_id} not found"}), 404

    db.session.commit()

    return jsonify({"message": f"{deleted_count} authors deleted successfully"}), 200

# Bulk Delete Books API
@app.route('/books/bulk', methods=['DELETE'])
def bulk_delete_books():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"message": "Request body must be a list of book IDs"}), 400

    deleted_count = 0
    for book_id in data:
        if not isinstance(book_id, int):
            return jsonify({"message": "Each book ID must be an integer"}), 400

        # Find the book by ID
        book = db.session.query(Book).get(book_id)
        
        if book:
            db.session.delete(book)
            deleted_count += 1
        else:
            return jsonify({"message": f"Book with ID {book_id} not found"}), 404

    db.session.commit()

    return jsonify({"message": f"{deleted_count} books deleted successfully"}), 200


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
```

### CRUD API Endpoints:

1. **Create Author** (`POST /authors`):
   - Adds a new author to the database.
   - Example request body:
     ```json
     {
       "name": "J.K. Rowling"
     }
     ```

2. **Create Book** (`POST /books`):
    - Adds a new book and associates it with an existing author.
    - Example request body:
     ```json
     {
          "title": "Harry Potter and the Philosopher Stone",
           "author_id": 1
     }

     ```


### Example Response:

```json
{
  "message": "Book created successfully",
  "book_id": 1
}
```

This ensures that the new book is created successfully, and the response will include the book's ID. Let me know if you need further clarification!


3. **Read Authors and Books** (`GET /search`):
   - Fetches authors and their books with filtering, sorting, and pagination.
   - Example query: `GET /search?author_name=Rowling&page=1&per_page=5&sort_by=author_name&sort_order=asc`
   - Returns a paginated list of authors and books with filtering by `author_name` or `book_title`.

4. **Update Author** (`PUT /authors/<int:id>`):
   - Updates the details of an existing author by ID.
   - Example request body:
     ```json
     {
       "name": "New Author Name"
     }
     ```

5. **Update Book** (`PUT /books/<int:id>`):
   - Updates the details of an existing book by ID.
   - Example request body:
     ```json
     {
       "title": "Updated Book Title",
       "author_id": 1
     }
     ```

6. **Delete Author** (`DELETE /authors/<int:id>`):
   - Deletes an author and all associated books by ID.

7. **Delete Book** (`DELETE /books/<int:id>`):
   - Deletes a book by ID.

### Example Request and Responses:

#### Create Author:
Request:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"name": "J.K. Rowling"}' http://localhost:5000/authors
```
Response:
```json
{
  "message": "Author created successfully",
  "author_id": 1
}
```

#### Create Book:
Request:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"title": "Harry Potter and the Philosophers Stone", "author_id": 1}' http://localhost:5000/books
```
Response:
```json
{
  "message": "Book created successfully",
  "book_id": 1
}
```

#### Update Author:
Request:
```bash
curl -X PUT -H "Content-Type: application/json" -d '{"name": "New Author Name"}' http://localhost:5000/authors/1
```
Response:
```json
{
  "message": "Author updated successfully",
  "author_id": 1
}
```

#### Delete Author:
Request:
```bash
curl -X DELETE http://localhost:5000/authors/1
```
Response:
```json
{
  "message": "Author and associated books deleted successfully"
}
```

### Sorting Parameters:
- **`sort_by`**: This can be either `author_name` or `book_title`.
- **`sort_order`**: This can be `asc` (ascending) or `desc` (descending).

### Updates for Sorting:
- We will apply sorting based on the provided `sort_by` and `sort_order` query parameters using SQLAlchemy's `order_by()` method.

1. **Sorting Parameters**:
   - **`sort_by`**: Specifies the field to sort by. You can choose either `author_name` or `book_title`.
   - **`sort_order`**: Specifies the order of sorting. It can be either `asc` (ascending) or `desc` (descending).

   Example query parameters for sorting:
   - `sort_by=author_name&sort_order=asc`
   - `sort_by=book_title&sort_order=desc`

2. **Sorting Logic**:
   - We check if `sort_by` is `author_name` or `book_title`.
   - Based on the value of `sort_order`, we apply either ascending (`asc()`) or descending (`desc()`) sorting on the appropriate field using SQLAlchemy's `order_by()` method.

3. **Pagination**:
   - The query uses `.paginate()` as before to limit the results to the current page and `per_page`.

4. **Response**:
   - The response now includes `sort_by` and `sort_order` metadata in addition to the pagination data (`page`, `per_page`, `total`, and `total_pages`).
   - It returns the sorted and paginated list of results under the `items` key.

### Example API Calls:

#### 1. Search and Sort by Author Name (Ascending Order):
```bash
curl "http://localhost:5000/search?author_name=Rowling&sort_by=author_name&sort_order=asc&page=1&per_page=5"
```

#### 2. Search and Sort by Book Title (Descending Order):
```bash
curl "http://localhost:5000/search?book_title=Harry Potter&sort_by=book_title&sort_order=desc&page=1&per_page=5"
```

### Example Response (Page 1, Sorted by Author Name, Ascending):

```json
{
  "page": 1,
  "per_page": 5,
  "total": 10,
  "total_pages": 2,
  "sort_by": "author_name",
  "sort_order": "asc",
  "items": [
    {
      "author_id": 1,
      "author_name": "J.K. Rowling",
      "book_id": 1,
      "book_title": "Harry Potter and the Philosopher's Stone"
    },
    {
      "author_id": 1,
      "author_name": "J.K. Rowling",
      "book_id": 2,
      "book_title": "Harry Potter and the Chamber of Secrets"
    }
  ]
}
```

### Notes:
- **Sorting**: You can change the sorting field and order by adjusting the `sort_by` and `sort_order` query parameters.
  - Example: `sort_by=book_title` will sort by the book title.
  - Example: `sort_order=desc` will sort in descending order.
- **Pagination**: The query results are paginated, so you can request specific pages of sorted data.
- **Defaults**: If no sorting or pagination parameters are provided, the system defaults to sorting by `author_name` in ascending order, and it returns the first page with 10 results.


### Notes:
- **CRUD operations** are integrated into the existing code with the use of `db.session.query` for querying and manipulating the database.
- **Error handling** is included for cases where the author or book does not exist when updating or deleting.


#### 1. Bulk Create Authors (`POST /authors/bulk`):
- Accepts a **list of authors** to be added to the database.
- Example request body:
  ```json
  [
    {"name": "J.K. Rowling"},
    {"name": "George R.R. Martin"},
    {"name": "J.R.R. Tolkien"}
  ]
  ```
- This will create three authors in one request.

#### 2. Bulk Create Books (`POST /books/bulk`):
- Accepts a **list of books** to be added to the database. Each book requires a `title` and `author_id`.
- Example request body:
  ```json
  [
    {"title": "Harry Potter and the Philosopher's Stone", "author_id": 1},
    {"title": "A Game of Thrones", "author_id": 2},
    {"title": "The Hobbit", "author_id": 3}
  ]
  ```
- This will create three books in one request, each linked to a valid author.

### Example `curl` Requests:

#### 1. Bulk Create Authors:
```bash
curl -X POST -H "Content-Type: application/json" -d '[{"name": "J.K. Rowling"},{"name": "George R.R. Martin"},{"name": "J.R.R. Tolkien"}]' http://localhost:5000/authors/bulk
```

#### 2. Bulk Create Books:
```bash
curl -X POST -H "Content-Type: application/json" -d '[{"title": "Harry Potter and the Philosophers Stone", "author_id": 1}, {"title": "A Game of Thrones", "author_id": 2}, {"title": "The Hobbit", "author_id": 3}]' http://localhost:5000/books/bulk
```

### Example Responses:

#### Response for Bulk Create Authors:
```json
{
  "message": "3 authors created successfully"
}
```

#### Response for Bulk Create Books:
```json
{
  "message": "3 books created successfully"
}
```

### Notes:
- **Bulk creation** is handled efficiently using `db.session.bulk_save_objects()`, which is optimized for inserting multiple records in one go.
- The request bodies must be **JSON arrays** containing multiple items, each representing an author or a book.
- **Error handling** is included to ensure that each request has valid data (e.g., authors must have a `name`, and books must have both a `title` and `author_id`).


### bulk update APIs:
1. **Bulk Update Authors** (`PUT /authors/bulk`):
   - Accepts a list of authors with their new names and updates them in the database based on their `id`.
2. **Bulk Update Books** (`PUT /books/bulk`):
   - Accepts a list of books with their new titles and updates them in the database based on their `id`.


### bulk update API Endpoints:

#### 1. Bulk Update Authors (`PUT /authors/bulk`):
- Accepts a **list of authors** where each author object contains an `id` and a `name`. It updates the names of authors based on their `id`.
- Example request body:
  ```json
  [
    {"id": 1, "name": "J.K. Rowling Updated"},
    {"id": 2, "name": "George R.R. Martin Updated"}
  ]
  ```
- This will update the names of authors with `id` 1 and 2.

#### 2. Bulk Update Books (`PUT /books/bulk`):
- Accepts a **list of books** where each book object contains an `id`, a `title`, and an `author_id`. It updates the books based on their `id`.
- Example request body:
  ```json
  [
    {"id": 1, "title": "Harry Potter and the Chamber of Secrets", "author_id": 1},
    {"id": 2, "title": "A Clash of Kings", "author_id": 2}
  ]
  ```
- This will update the title and author for the books with `id` 1 and 2.

### Example `curl` Requests:

#### 1. Bulk Update Authors:
```bash
curl -X PUT -H "Content-Type: application/json" -d '[{"id": 1, "name": "J.K. Rowling Updated"},{"id": 2, "name": "George R.R. Martin Updated"}]' http://localhost:5000/authors/bulk
```

#### 2. Bulk Update Books:
```bash
curl -X PUT -H "Content-Type: application/json" -d '[{"id": 1, "title": "Harry Potter and the Chamber of Secrets", "author_id": 1}, {"id": 2, "title": "A Clash of Kings", "author_id": 2}]' http://localhost:5000/books/bulk
```

### Example Responses:

#### Response for Bulk Update Authors:
```json
{
  "message": "2 authors updated successfully"
}
```

#### Response for Bulk Update Books:
```json
{
  "message": "2 books updated successfully"
}
```

### Notes:
- **Bulk updating** is handled using a loop to process each item and update the respective record in the database.
- **Error handling** ensures that each request has valid data (e.g., each author or book must have `id` and other necessary fields).
- If a book or author with a specified `id` does not exist, an error response will be returned indicating the specific item that could not be found.

### Bulk delete APIs:
1. **Bulk Delete Authors** (`DELETE /authors/bulk`):
   - Accepts a list of author IDs and deletes the corresponding authors from the database.
2. **Bulk Delete Books** (`DELETE /books/bulk`):
   - Accepts a list of book IDs and deletes the corresponding books from the database.

### Bulk Delete API Endpoints:

#### 1. Bulk Delete Authors (`DELETE /authors/bulk`):
- Accepts a **list of author IDs** and deletes the corresponding authors from the database.
- Example request body:
  ```json
  [1, 2, 3]
  ```
- This will delete the authors with IDs 1, 2, and 3.

#### 2. Bulk Delete Books (`DELETE /books/bulk`):
- Accepts a **list of book IDs** and deletes the corresponding books from the database.
- Example request body:
  ```json
  [1, 2, 3]
  ```
- This will delete the books with IDs 1, 2, and 3.

### Example `curl` Requests:

#### 1. Bulk Delete Authors:
```bash
curl -X DELETE -H "Content-Type: application/json" -d '[1, 2, 3]' http://localhost:5000/authors/bulk
```

#### 2. Bulk Delete Books:
```bash
curl -X DELETE -H "Content-Type: application/json" -d '[1, 2, 3]' http://localhost:5000/books/bulk
```

### Example Responses:

#### Response for Bulk Delete Authors:
```json
{
  "message": "3 authors deleted successfully"
}
```

#### Response for Bulk Delete Books:
```json
{
  "message": "3 books deleted successfully"
}
```

### Notes:
- **Bulk deletion** is handled by iterating over the list of IDs and deleting the corresponding records.
- If any author or book with the specified `id` does not exist, an error response is returned indicating the specific item that could not be found.
- We check if the IDs are valid integers to ensure data consistency.

