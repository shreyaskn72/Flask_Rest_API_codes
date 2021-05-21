from flask import Blueprint

from flask import request

from flask import url_for, render_template_string

from api.utils.responses import response_with

from api.utils import responses as resp

from api.models.users import User

from api.utils.database import db

from api.models.users import User, app, auth

from flask import Flask, abort, request, jsonify, g, url_for

from flask_jwt_extended import create_access_token


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



