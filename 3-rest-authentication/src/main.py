import os
from api.config.config import DevelopmentConfig, ProductionConfig, TestingConfig
from flask import Flask
from api.utils.database import db

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

# endpoint for authentication
app.register_blueprint(user_routes, url_prefix='/api/users/')


db.init_app(app)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
