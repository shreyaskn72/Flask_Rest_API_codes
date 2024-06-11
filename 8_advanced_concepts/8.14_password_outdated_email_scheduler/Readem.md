# Password Expiration Reminder

This is a Flask application that includes a Celery task scheduler to remind users to change their passwords when they are about to expire.

## Installation

1. Clone the repository:



2. install required modules:

```
pip install flask flask_sqlalchemy flask_mail celery redis
```

3. Configure the Flask app:

    - Set up your database URI in the Flask app configuration (app.config['SQLALCHEMY_DATABASE_URI']).
    - Configure your email server settings in the Flask app configuration (app.config['MAIL_SERVER'], app.config['MAIL_PORT'], app.config['MAIL_USE_TLS'], app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']).


4. Run the Celery worker and beat scheduler:
```bash
celery -A app.celery worker --loglevel=INFO
```
```
celery -A app.celery beat --loglevel=INFO
```

