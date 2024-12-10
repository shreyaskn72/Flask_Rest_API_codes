import logging
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Initialize SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre
        }

# Create database tables
db.create_all()

# Routes
@app.route('/books', methods=['GET'])
def get_books():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        title = request.args.get('title', '')
        author = request.args.get('author', '')
        genre = request.args.get('genre', '')

        query = Book.query

        if title:
            query = query.filter(Book.title.ilike(f'%{title}%'))
        if author:
            query = query.filter(Book.author.ilike(f'%{author}%'))
        if genre:
            query = query.filter(Book.genre.ilike(f'%{genre}%'))

        books = query.paginate(page, page_size, False)

        return jsonify({
            'books': [book.serialize() for book in books.items],
            'total_books': books.total,
            'total_pages': books.pages,
            'current_page': books.page
        }), 200
    except SQLAlchemyError as e:
        logging.error(f'Database error: {str(e)}')
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 400

@app.route('/books', methods=['POST'])
def add_book():
    try:
        data = request.json
        if 'title' not in data or 'author' not in data or 'genre' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        new_book = Book(title=data['title'], author=data['author'], genre=data['genre'])
        db.session.add(new_book)
        db.session.commit()

        return jsonify(new_book.serialize()), 201
    except SQLAlchemyError as e:
        logging.error(f'Database error: {str(e)}')
        db.session.rollback()
        return jsonify({'message': 'Database error', 'error':str(e)}), 500
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
