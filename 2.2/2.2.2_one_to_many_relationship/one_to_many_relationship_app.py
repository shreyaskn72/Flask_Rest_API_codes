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