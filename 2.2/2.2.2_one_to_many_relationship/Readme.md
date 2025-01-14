Below is the full code that includes the ability to **create**, **update**, and **delete** authors and books, along with the previous functionality for demonstrating the `JOIN`. Additionally, I'll provide the `curl` commands for all the endpoints to perform the operations.

### Full Flask API Code:

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

if __name__ == '__main__':
    app.run(debug=True)
```

### Explanation:
1. **GET `/authors_with_books`:** Returns authors with their books and the join columns (i.e., `author_id` and `book_author_id`).
2. **POST `/authors`:** Allows you to create a new author.
3. **PUT `/authors/<id>`:** Allows you to update an existing author by ID.
4. **DELETE `/authors/<id>`:** Deletes an author by ID.
5. **POST `/books`:** Allows you to create a new book associated with an author.
6. **PUT `/books/<id>`:** Allows you to update an existing book by ID.
7. **DELETE `/books/<id>`:** Deletes a book by ID.

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

### Running the Application:

1. Make sure you have Flask and SQLAlchemy installed:
   ```bash
   pip install Flask SQLAlchemy
   ```

2. Run the Flask app:
   ```bash
   python app.py
   ```

3. The Flask app will be running on `http://127.0.0.1:5000`.

Now you can use the provided `curl` commands to interact with your API!