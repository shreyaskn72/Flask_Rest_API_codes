from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db = SQLAlchemy(app)

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Book(title={self.title}, author={self.author}, genre={self.genre})"

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

# Create the database tables
db.create_all()

# Create some sample data
sample_data = [
    {"title": "Book 1", "author": "Author 1", "genre": "Fiction"},
    {"title": "Book 2", "author": "Author 2", "genre": "Non-Fiction"},
    {"title": "Book 3", "author": "Author 3", "genre": "Fiction"},
    # Add more books here
]

for data in sample_data:
    book = Book(**data)
    db.session.add(book)

db.session.commit()

# Pagination parameters
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10

@app.route('/books', methods=['GET'])
def get_books():
    # Pagination
    page = int(request.args.get('page', DEFAULT_PAGE))
    page_size = int(request.args.get('page_size', DEFAULT_PAGE_SIZE))
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    # Querying books from the database
    query = Book.query

    # Filtering
    title = request.args.get('title')
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))
    author = request.args.get('author')
    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))
    genre = request.args.get('genre')
    if genre:
        query = query.filter(Book.genre.ilike(f'%{genre}%'))

    # Sorting
    sort_by = request.args.get('sort_by')
    if sort_by:
        if sort_by.startswith('-'):
            sort_by = sort_by[1:]
            query = query.order_by(getattr(Book, sort_by).desc())
        else:
            query = query.order_by(getattr(Book, sort_by))

    # Paginate the filtered and sorted books
    books = query.slice(start_index, end_index).all()

    # Serialize books to dictionary format
    books_json = [book.to_dict() for book in books]

    return jsonify(books_json)

if __name__ == '__main__':
    app.run(debug=True)
