from flask import Blueprint

from flask import request

from api.utils.responses import response_with

from api.models.directors import Director, DirectorSchema

from api.utils import responses as resp

from api.models.directors import Director, DirectorSchema

from api.utils.database import db


director_routes = Blueprint("director_routes", __name__)


@director_routes.route('/', methods=['POST'])

def create_director():

    try:

        data = request.get_json()

        director_schema = DirectorSchema()

        director = director_schema.load(data)

        result = director_schema.dump(director.create())

        return response_with(resp.SUCCESS_201, value={"director": result})

    except Exception as e:

        return response_with(resp.INVALID_INPUT_422)

@director_routes.route('/', methods=['GET'])

def get_director_list():

    fetched = Director.query.all()

    director_schema = DirectorSchema(many=True, only=['first_name', 'last_name', 'id'])

    directors = director_schema.dump(fetched)

    return response_with(resp.SUCCESS_200, value={"directors": directors})


@director_routes.route('/<int:director_id>', methods=['GET'])

def get_director_detail(director_id):

    fetched = Director.query.get_or_404(director_id)

    director_schema = DirectorSchema()

    director = director_schema.dump(fetched)

    return response_with(resp.SUCCESS_200, value={"director": director})


@director_routes.route('/<int:id>', methods=['PUT'])
def update_director_detail(id):
    data = request.get_json()
    get_director = Director.query.get_or_404(id)
    get_director.first_name = data['first_name']
    get_director.last_name = data['last_name']
    db.session.add(get_director)
    db.session.commit()
    director_schema = DirectorSchema()
    director = director_schema.dump(get_director)
    return response_with(resp.SUCCESS_200, value={"director": director})


@director_routes.route('/<int:id>', methods=['PATCH'])

def modify_director_detail(id):

    data = request.get_json()

    get_director = Director.query.get(id)

    if data.get('first_name'):

        get_director.first_name = data['first_name']

    if data.get('last_name'):

        get_director.last_name = data['last_name']

    db.session.add(get_director)

    db.session.commit()

    director_schema = DirectorSchema()

    director = director_schema.dump(get_director)

    return response_with(resp.SUCCESS_200, value={"director": director})


@director_routes.route('/<int:id>', methods=['DELETE'])

def delete_director(id):

    get_director = Director.query.get_or_404(id)
    db.session.delete(get_director)
    db.session.commit()
    return response_with(resp.SUCCESS_204)