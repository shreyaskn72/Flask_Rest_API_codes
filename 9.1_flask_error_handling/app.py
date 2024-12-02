import logging
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import RequestTimeout

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

# Error handlers
@app.errorhandler(IndexError)
def handle_index_error(e):
    logging.exception('An IndexError occurred: %s', e)
    return jsonify({'error': 'IndexError', 'message': str(e)}), 400

@app.errorhandler(KeyError)
def handle_key_error(e):
    logging.exception('A KeyError occurred: %s', e)
    return jsonify({'error': 'KeyError', 'message': str(e)}), 400

@app.errorhandler(ValueError)
def handle_value_error(e):
    logging.exception('A ValueError occurred: %s', e)
    return jsonify({'error': 'ValueError', 'message': str(e)}), 400

@app.errorhandler(TypeError)
def handle_type_error(e):
    logging.exception('A TypeError occurred: %s', e)
    return jsonify({'error': 'TypeError', 'message': str(e)}), 400

@app.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(e):
    logging.exception('A SQLAlchemyError occurred: %s', e)
    return jsonify({'error': 'SQLAlchemyError', 'message': str(e), 'args': str(e.args)}), 500

@app.errorhandler(UnicodeError)
def handle_unicode_error(e):
    logging.exception('A UnicodeError occurred: %s', e)
    return jsonify({'error': 'UnicodeError', 'message': str(e)}), 400

@app.errorhandler(AttributeError)
def handle_attribute_error(e):
    logging.exception('An AttributeError occurred: %s', e)
    return jsonify({'error': 'AttributeError', 'message': str(e)}), 400




#Triggered when an assert statement fails.
@app.errorhandler(AssertionError)
def handle_assertion_error(e):
    logging.exception('An AssertionError occurred: %s', str(e))
    return jsonify({'error': 'AssertionError', 'message': str(e)}), 500


""""
FileNotFoundError
Raised when a file or directory is requested but cannot be found.
"""
@app.errorhandler(FileNotFoundError)
def handle_file_not_found_error(e):
    logging.exception('A FileNotFoundError occurred: %s', str(e))
    return jsonify({'error': 'FileNotFoundError', 'message': str(e)}), 404


"""
IOError
Raised when an input/output operation (such as file operation) fails.
"""
@app.errorhandler(IOError)
def handle_io_error(e):
    logging.exception('An IOError occurred: %s', str(e))
    return jsonify({'error': 'IOError', 'message': str(e)}), 500
"""
RequestTimeout
Specific HTTP exception indicating a client request timed out.
"""


@app.errorhandler(RequestTimeout)
def handle_request_timeout(e):
    logging.exception('A RequestTimeout occurred: %s', str(e))
    return jsonify({'error': 'RequestTimeout', 'message': 'The request timed out'}), 408


#For all other unhandled error
@app.errorhandler(Exception)
def handle_generic_error(e):
    if isinstance(e, SQLAlchemyError):
        logging.exception('A SQLAlchemyError occurred: %s', e)
        return jsonify({'error': 'SQLAlchemyError', 'message': str(e), 'args': str(e.args)}), 500

    elif isinstance(e, HTTPException):
        status_code = e.code
        error_name = e.name
    else:
        status_code = 500
        error_name = 'Internal Server Error'

    logging.exception('%s occurred: %s', error_name, str(e))
    return jsonify({'error': error_name, 'message': str(e)}), status_code

"""
Custom Exception Handling:

You can also handle custom exceptions by defining your own exception classes and using @app.errorhandler to catch them.
"""

#Define CustomException class
class CustomException(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

# Custom error handler for specific exceptions
@app.errorhandler(CustomException)
def handle_custom_exception(e):
    logging.exception('A CustomException occurred: %s', e.message)
    return jsonify({'error': 'CustomError', 'message': e.message, 'success': False}), e.status_code



# API endpoint to add an item via POST request
@app.route('/api/add_item', methods=['POST'])
def add_item():
    data = request.json
    name = data['name']
    quantity = data['quantity']

    # Error handling for missing fields using CustomException
    if not name or not quantity:
        raise CustomException('Missing required fields', 400)

    # Insert item into database
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
