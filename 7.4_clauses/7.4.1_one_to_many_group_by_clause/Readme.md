Certainly! To include a `GROUP BY` functionality, let's create an API that groups the books by their author and returns the count of books per author. This will demonstrate how to use SQLAlchemy's `group_by()` method.

I'll modify the existing code to add this new API endpoint.

### Full Flask API Code with `GROUP BY`:

```python
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask app and the SQLAlchemy object
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books_authors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Author and Book models
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', backref='author', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

# Initialize the database (you only need to run this once)
with app.app_context():
    db.create_all()

# API endpoint to demonstrate JOIN
@app.route('/authors_with_books', methods=['GET'])
def get_authors_with_books():
    # Perform a SQL JOIN using SQLAlchemy ORM relationship
    authors_with_books = db.session.query(
        Author.id.label('author_id'), 
        Author.name.label('author_name'),
        Book.id.label('book_id'),
        Book.title.label('book_title'),
        Book.author_id.label('book_author_id')  # This is the join column
    ).join(Book, Author.id == Book.author_id).all()  # Explicitly specifying join condition
    
    # Format the result as JSON including join columns (author and book details)
    result = []
    for row in authors_with_books:
        result.append({
            'author_id': row.author_id,
            'author_name': row.author_name,
            'book_id': row.book_id,
            'book_title': row.book_title,
            'book_author_id': row.book_author_id  # This shows the column used in JOIN
        })
    
    return jsonify(result)

# Create a new author
@app.route('/authors', methods=['POST'])
def create_author():
    data = request.get_json()
    if not data or not data.get('name'):
        abort(400, 'Author name is required')
    
    new_author = Author(name=data['name'])
    db.session.add(new_author)
    db.session.commit()
    return jsonify({'id': new_author.id, 'name': new_author.name}), 201

# Update an existing author
@app.route('/authors/<int:id>', methods=['PUT'])
def update_author(id):
    author = Author.query.get(id)
    if not author:
        abort(404, 'Author not found')
    
    data = request.get_json()
    if data.get('name'):
        author.name = data['name']
    
    db.session.commit()
    return jsonify({'id': author.id, 'name': author.name})

# Delete an author
@app.route('/authors/<int:id>', methods=['DELETE'])
def delete_author(id):
    author = Author.query.get(id)
    if not author:
        abort(404, 'Author not found')
    
    db.session.delete(author)
    db.session.commit()
    return jsonify({'message': 'Author deleted successfully'})

# Create a new book
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('author_id'):
        abort(400, 'Book title and author_id are required')
    
    author = Author.query.get(data['author_id'])
    if not author:
        abort(404, 'Author not found')
    
    new_book = Book(title=data['title'], author_id=data['author_id'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'id': new_book.id, 'title': new_book.title, 'author_id': new_book.author_id}), 201

# Update an existing book
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)
    if not book:
        abort(404, 'Book not found')
    
    data = request.get_json()
    if data.get('title'):
        book.title = data['title']
    
    db.session.commit()
    return jsonify({'id': book.id, 'title': book.title, 'author_id': book.author_id})

# Delete a book
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        abort(404, 'Book not found')
    
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})

# API endpoint for GROUP BY to count books per author
@app.route('/authors_books_count', methods=['GET'])
def authors_books_count():
    # Perform a GROUP BY query to count books per author
    result = db.session.query(
        Author.id.label('author_id'),
        Author.name.label('author_name'),
        db.func.count(Book.id).label('book_count')
    ).join(Book, Author.id == Book.author_id).group_by(Author.id).all()
    
    # Format the result as JSON
    authors_books = []
    for row in result:
        authors_books.append({
            'author_id': row.author_id,
            'author_name': row.author_name,
            'book_count': row.book_count
        })
    
    return jsonify(authors_books)

if __name__ == '__main__':
    app.run(debug=True)
```

### Key Addition:
- **GET `/authors_books_count`:** This new endpoint demonstrates how to use `GROUP BY` in SQLAlchemy. It groups the authors by their ID and counts how many books each author has. We use the `db.func.count(Book.id)` to get the number of books per author.

### Example Database Setup:
Let’s assume the following data in the database:

- **Authors:**
  - 1: J.K. Rowling
  - 2: George R.R. Martin

- **Books:**
  - 1: Harry Potter and the Sorcerer's Stone (author_id 1)
  - 2: Game of Thrones (author_id 2)
  - 3: Harry Potter and the Chamber of Secrets (author_id 1)

### Example Response for `GET /authors_books_count`:

This endpoint will return the count of books for each author:

```json
[
    {
        "author_id": 1,
        "author_name": "J.K. Rowling",
        "book_count": 2
    },
    {
        "author_id": 2,
        "author_name": "George R.R. Martin",
        "book_count": 1
    }
]
```

### Curl Commands:

1. **GET `/authors_with_books`**: Fetch authors with their books and join columns.
   ```bash
   curl -X GET http://127.0.0.1:5000/authors_with_books
   ```

2. **POST `/authors`**: Create a new author.
   ```bash
   curl -X POST http://127.0.0.1:5000/authors -H "Content-Type: application/json" -d '{"name": "J.K. Rowling"}'
   ```

3. **PUT `/authors/<id>`**: Update an existing author (replace `<id>` with the author ID).
   ```bash
   curl -X PUT http://127.0.0.1:5000/authors/1 -H "Content-Type: application/json" -d '{"name": "J.K. Rowling Updated"}'
   ```

4. **DELETE `/authors/<id>`**: Delete an author by ID.
   ```bash
   curl -X DELETE http://127.0.0.1:5000/authors/1
   ```

5. **POST `/books`**: Create a new book (replace `author_id` with a valid author ID).
   ```bash
   curl -X POST http://127.0.0.1:5000/books -H "Content-Type: application/json" -d '{"title": "Harry Potter and the Chamber of Secrets", "author_id": 1}'
   ```

6. **PUT `/books/<id>`**: Update an existing book (replace `<id>` with the book ID).
   ```bash
   curl -X PUT http://127.0.0.1:5000/books/1 -H "Content-Type: application/json" -d '{"title": "Harry Potter and the Prisoner of Azkaban"}'
   ```

7. **DELETE `/books/<id>`**: Delete a book by ID.
   ```bash
   curl -X DELETE http://127.0.0.1:5000/books/1
   ```

8. **GET `/authors_books_count`**: Get the count of books for each author.
   ```bash
   curl -X GET http://127.0.0.1:5000/authors_books_count
   ```

### Running the Application:

1. Ensure Flask and SQLAlchemy are installed:
   ```bash
   pip install Flask SQLAlchemy
   ```

2. Run the Flask application:
   ```bash
   python app.py
   ```

3. The Flask app will run at `http://127.0.0.1:5000`, and you can test all the APIs using the provided `curl` commands.

This setup now includes the `GROUP BY` functionality and demonstrates how to aggregate data (counting books per author).