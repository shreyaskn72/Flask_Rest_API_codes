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
