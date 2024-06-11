from flask import Flask, request, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_logs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_logs = db.relationship('UserLog', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# UserLog model
class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"UserLog('{self.ip_address}', '{self.timestamp}', '{self.user_id}')"

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully.'}), 200

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        ip_address = request.remote_addr
        new_log = UserLog(ip_address=ip_address, user_id=user.id)
        db.session.add(new_log)
        db.session.commit()
        return jsonify({'message': 'Logged in successfully.'}), 200
    return jsonify({'message': 'Invalid username or password.'}), 401

# Route to get user logs
@app.route('/user_logs', methods=['GET'])
def get_user_logs():
    logs = UserLog.query.all()
    logs_list = [{'id': log.id, 'ip_address': log.ip_address, 'timestamp': log.timestamp, 'user_id': log.user_id} for log in logs]
    return jsonify(logs_list), 200




# Route to get all IP addresses of a particular user
@app.route('/user/<int:user_id>/logs', methods=['GET'])
def get_user_id_logs(user_id):
    user = User.query.get_or_404(user_id)
    user_logs = UserLog.query.filter_by(user_id=user_id).all()
    logs_list = [{'id': log.id, 'timestamp': log.timestamp, 'ip_address': log.ip_address} for log in user_logs]
    return jsonify({'user_id': user_id, 'logs': logs_list}), 200

if __name__ == '__main__':
    # Create database tables before running the app
    db.create_all()
    app.run(debug=True)
