from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.movies import Movie, MovieSchema

from api.utils.database import db

movie_routes = Blueprint("movie_routes", __name__)


@movie_routes.route('/', methods=['POST'])

def create_movie():

    try:
        data = request.get_json()
        movie_schema = MovieSchema()
        movie = movie_schema.load(data)
        result = movie_schema.dump(movie.create())
        return response_with(resp.SUCCESS_201, value={"movie": result})

    except Exception as e:

        print(e)

        return response_with(resp.INVALID_INPUT_422)



@movie_routes.route('/', methods=['GET'])

def get_movie_list():
    fetched = Movie.query.all()
    movie_schema = MovieSchema(many=True, only=['director_id','title', 'year'])
    movies = movie_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={"movies": movies})



@movie_routes.route('/<int:id>', methods=['GET'])
def get_movie_detail(id):
    fetched = Movie.query.get_or_404(id)
    movie_schema = MovieSchema()
    movies = movie_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={"movies": movies})


@movie_routes.route('/<int:id>', methods=['PUT'])

def update_movie_detail(id):
    data = request.get_json()
    get_movie = Movie.query.get_or_404(id)
    get_movie.title = data['title']
    get_movie.year = data['year']
    db.session.add(get_movie)
    db.session.commit()
    movie_schema = MovieSchema()
    movie = movie_schema.dump(get_movie)
    return response_with(resp.SUCCESS_200, value={"movie": movie})



@movie_routes.route('/<int:id>', methods=['PATCH'])

def modify_movie_detail(id):

    data = request.get_json()
    get_movie = Movie.query.get_or_404(id)

    if data.get('title'):
        get_movie.title = data['title']

    if data.get('year'):
        get_movie.year = data['year']

    db.session.add(get_movie)
    db.session.commit()
    movie_schema = MovieSchema()

    movie = movie_schema.dump(get_movie)

    return response_with(resp.SUCCESS_200, value={"movie": movie})



@movie_routes.route('/<int:id>', methods=['DELETE'])
def delete_movie(id):

    get_movie = Movie.query.get_or_404(id)
    db.session.delete(get_movie)
    db.session.commit()
    return response_with(resp.SUCCESS_204)