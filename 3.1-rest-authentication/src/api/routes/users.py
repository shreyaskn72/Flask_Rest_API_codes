from flask import Blueprint


from api.utils.database import db

from api.models.users import User, app, auth

from flask import Flask, abort, request, jsonify, g, url_for


user_routes = Blueprint("user_routes", __name__)


@user_routes.route('/', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}))
            #{'Location': url_for('user_routes.get_user', id=user.id, _external=True)})


@user_routes.route('<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

"""
@user_routes.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token, 'duration': 600})
"""


@user_routes.route('/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})
