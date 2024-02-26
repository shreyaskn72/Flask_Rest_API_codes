# Import Flask and SQLAlchemy
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Create a Flask app and configure the database URI
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create a SQLAlchemy object and a database model
db = SQLAlchemy(app)

class Movie(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  year = db.Column(db.Integer, nullable=False)
  rating = db.Column(db.Float, nullable=False)

  def __repr__(self):
   return f"<Movie {self.title}>"

  def to_dict(self):
   return {
     "id": self.id,
     "title": self.title,
     "year": self.year,
     "rating": self.rating
    }



# Define a route for the movies endpoint
@app.route("/movies")
def movies():
    # Get the query parameters
    page = request.args.get("page", 1, type=int)  # the current page number
    per_page = request.args.get("per_page", 5, type=int)  # the number of items per page
    filter = request.args.get("filter", None, type=str)  # the filter keyword
    sort = request.args.get("sort", None, type=str)  # the sort column
    order = request.args.get("order", "asc", type=str)  # the sort order

    # Get the movies from the database
    movies = Movie.query

    # Apply the filter if provided
    if filter:
        movies = movies.filter(Movie.title.contains(filter))

    # Apply the sort if provided
    if sort:
        if sort == "title":
            movies = movies.order_by(Movie.title.asc() if order == "asc" else Movie.title.desc())

        elif sort == "year":
            movies = movies.order_by(Movie.year.asc() if order == "asc" else Movie.year.desc())
        elif sort == "rating":
            movies = movies.order_by(Movie.rating.asc() if order == "asc" else Movie.rating.desc())


    # Apply the pagination
    movies = movies.paginate(page=page, per_page=per_page, error_out=False)

    # Convert the movies to a list of dictionaries
    movies = [movie.to_dict() for movie in movies.items]

    # Return the JSON response
    return jsonify({
        "success": True,
        "movies": movies,
        "total": len(movies)
    })






# Run the app
if __name__ == "__main__":
    with app.app_context():
        # Create some sample data
        db.drop_all()
        db.create_all()
        db.session.add(Movie(title="The Godfather", year=1972, rating=9.2))
        db.session.add(Movie(title="The Shawshank Redemption", year=1994, rating=9.3))
        db.session.add(Movie(title="The Dark Knight", year=2008, rating=9.0))
        db.session.add(Movie(title="The Matrix", year=1999, rating=8.7))
        db.session.add(Movie(title="Inception", year=2010, rating=8.8))
        db.session.add(Movie(title="The Lord of the Rings: The Return of the King", year=2003, rating=8.9))
        db.session.add(Movie(title="The Lion King", year=1994, rating=8.5))
        db.session.add(Movie(title="The Avengers", year=2012, rating=8.0))
        db.session.add(Movie(title="Titanic", year=1997, rating=7.8))
        db.session.add(Movie(title="Avatar", year=2009, rating=7.8))
        db.session.commit()
    app.run(debug=True)

"""
This program creates a SQLite database with a table named Movie, and inserts some sample data into it. Then, it defines a route for the /movies endpoint, which accepts query parameters for page, per_page, filter, sort, and order. It uses the SQLAlchemy methods to query, filter, sort, and paginate the movies from the database, and returns them as a JSON response.

You can test the program by running it and sending requests to the /movies endpoint with different query parameters. For example, you can use curl to send requests like this:

# Get the first page of movies with 5 items per page
curl http://localhost:5000/movies

# Get the second page of movies with 3 items per page
curl http://localhost:5000/movies?page=2&per_page=3

# Get the movies that contain the word "The" in their title
curl http://localhost:5000/movies?filter=The

# Get the movies sorted by rating in descending order
curl http://localhost:5000/movies?sort=rating&order=desc

You can also use a web browser or a tool like Postman to send requests and view the responses.

"""