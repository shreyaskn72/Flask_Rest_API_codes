from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
#jwt_refresh_token_required#@jwt_required(refresh=True)
from datetime import datetime, timedelta

app = Flask(__name__)

# Secret key for JWT
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this to a long random string in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

jwt = JWTManager(app)

# Mock user database
users = {
    'user1': {
        'password': 'password1'
    }
}


# Authentication endpoint to generate tokens
@app.route('/auth', methods=['POST'])
def auth():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        return jsonify({'msg': 'Missing username or password'}), 400

    if username not in users or users[username]['password'] != password:
        return jsonify({'msg': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    # Expiry time for access token
    access_token_expiry = datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']

    # Expiry time for refresh token
    refresh_token_expiry = datetime.utcnow() + app.config['JWT_REFRESH_TOKEN_EXPIRES']

    return jsonify(
        access_token=access_token,
        access_token_expiry=access_token_expiry,
        refresh_token=refresh_token,
        refresh_token_expiry=refresh_token_expiry
    ), 200


# Protected endpoint
@app.route('/hello', methods=['GET'])
@jwt_required()
def hello():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user, message='Hello, World!')


# Refresh token endpoint
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)

    # Expiry time for new access token
    new_access_token_expiry = datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']

    return jsonify(access_token=new_access_token, access_token_expiry=new_access_token_expiry), 200


if __name__ == '__main__':
    app.run(debug=True)
