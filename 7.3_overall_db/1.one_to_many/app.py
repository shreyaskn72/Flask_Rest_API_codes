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


# Bulk Update Authors API
@app.route('/authors/bulk', methods=['PUT'])
def bulk_update_authors():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"message": "Request body must be a list of authors"}), 400

    updated_count = 0
    for author_data in data:
        author_id = author_data.get('id')
        new_name = author_data.get('name')

        if not author_id or not new_name:
            return jsonify({"message": "Each author must have 'id' and 'name' fields"}), 400

        # Find the author by ID
        author = db.session.query(Author).get(author_id)

        if author:
            author.name = new_name
            updated_count += 1
        else:
            return jsonify({"message": f"Author with ID {author_id} not found"}), 404

    db.session.commit()

    return jsonify({"message": f"{updated_count} authors updated successfully"}), 200


# Bulk Update Books API
@app.route('/books/bulk', methods=['PUT'])
def bulk_update_books():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"message": "Request body must be a list of books"}), 400

    updated_count = 0
    for book_data in data:
        book_id = book_data.get('id')
        new_title = book_data.get('title')
        new_author_id = book_data.get('author_id')

        if not book_id or not new_title or not new_author_id:
            return jsonify({"message": "Each book must have 'id', 'title', and 'author_id' fields"}), 400

        # Find the book by ID
        book = db.session.query(Book).get(book_id)

        if book:
            book.title = new_title
            book.author_id = new_author_id
            updated_count += 1
        else:
            return jsonify({"message": f"Book with ID {book_id} not found"}), 404

    db.session.commit()

    return jsonify({"message": f"{updated_count} books updated successfully"}), 200


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