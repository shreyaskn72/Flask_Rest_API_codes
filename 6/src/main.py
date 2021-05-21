from flask import Flask
from flask import jsonify
from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp
import os
from api.config.config import DevelopmentConfig, ProductionConfig, TestingConfig
import logging
from api.routes.directors import director_routes
from api.routes.movies import movie_routes

# authentication imports
from api.routes.users import user_routes

app = Flask(__name__)


if os.environ.get('WORK_ENV') == 'PROD':
    app_config = ProductionConfig

elif os.environ.get('WORK_ENV') == 'TEST':
    app_config = TestingConfig

else:
    app_config = DevelopmentConfig

app.config.from_object(app_config)

db.init_app(app)
with app.app_context():
    db.create_all()


app.register_blueprint(director_routes, url_prefix='/api/directors/')
app.register_blueprint(movie_routes, url_prefix='/api/movies/')

# endpoint for authentication
app.register_blueprint(user_routes, url_prefix='/api/users/')

# START GLOBAL HTTP CONFIGURATIONS
@app.after_request
def add_header(response):
    return response

@app.errorhandler(400)
def bad_request(e):
    logging.error(e)
    return response_with(resp.BAD_REQUEST_400)


@app.errorhandler(500)
def server_error(e):
    logging.error(e)
    return response_with(resp.SERVER_ERROR_500)

@app.errorhandler(404)
def not_found(e):
    logging.error(e)
    return response_with(resp.SERVER_ERROR_404)

db.init_app(app)
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", use_reloader=False)
