from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_logs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'

db = SQLAlchemy(app)
mail = Mail(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    password_last_changed = db.Column(db.DateTime, nullable=False, default=datetime.now)

@celery.task
def send_password_expiry_email(user_email):
    msg = Message('Password Expiry Reminder', recipients=[user_email])
    msg.body = "Your password is about to expire. Please change it to continue accessing your account."
    try:
        mail.send(msg)
        print("Password expiry email sent successfully to", user_email)
    except Exception as e:
        print("Error sending password expiry email to", user_email, ":", str(e))

@celery.beat(schedule=crontab(hour=0, minute=0))
def schedule_password_expiry_emails():
    users = User.query.all()
    for user in users:
        days_until_expiry = (user.password_last_changed + timedelta(days=90)) - datetime.now()
        if days_until_expiry.days == 5:
            send_password_expiry_email.delay(user.email)

if __name__ == '__main__':
    app.run(debug=True)
