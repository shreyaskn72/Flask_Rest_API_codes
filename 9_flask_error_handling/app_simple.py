import logging
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.exceptions import HTTPException

# Define CustomException class
class CustomException(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

# Initialize Flask application
app = Flask(__name__)

# SQLAlchemy setup
DATABASE_URL = 'sqlite:///:memory:'
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

# Define a simple data model
class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    quantity = Column(Integer)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Setup logging
logging.basicConfig(level=logging.ERROR)

# Custom error handler for specific exceptions
@app.errorhandler(CustomException)
def handle_custom_exception(e):
    logging.exception('A CustomException occurred: %s', e.message)
    return jsonify({'error': 'CustomError', 'message': e.message, 'success': False}), e.status_code

# Global error handler for all exceptions
@app.errorhandler(Exception)
def handle_generic_error(e):
    if isinstance(e, SQLAlchemyError):
        logging.exception('A SQLAlchemyError occurred: %s', e)
        return jsonify({'error': 'SQLAlchemyError', 'message': str(e)}), 500

    elif isinstance(e, HTTPException):
        status_code = e.code
        error_name = e.name
    else:
        status_code = 500
        error_name = 'Internal Server Error'

    logging.exception('%s occurred: %s', error_name, str(e))
    return jsonify({'error': error_name, 'message': str(e)}), status_code

# API endpoint to add an item via POST request
@app.route('/api/add_item', methods=['POST'])
def add_item():
    data = request.json
    name = data.get('name')
    quantity = data.get('quantity')

    #Error handling for missing fields using CustomException
    if not name or not quantity:
        raise CustomException('Missing required fields', 400)

    # Insert item into database (dummy code for demonstration)
    # Replace with your actual database logic
    session = Session()
    item = Item(name=name, quantity=quantity)
    session.add(item)
    session.commit()
    session.close()

    return jsonify({'message': 'Item added successfully'}), 201


@app.route('/api/hello', methods=['GET'])
def hello():
    print("hello")


if __name__ == '__main__':
    app.run()
