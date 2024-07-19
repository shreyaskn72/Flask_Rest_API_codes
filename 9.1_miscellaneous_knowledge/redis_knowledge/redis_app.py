from flask import Flask
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config['REDIS_URL'] = "redis://localhost:6379/0"
redis_client = FlaskRedis(app)

@app.route('/data')
def get_data():
    cached_data = redis_client.get('cached_data')
    if cached_data:
        return cached_data

    # Fetch data from MySQL or other source
    data = fetch_data_from_mysql()

    # Store data in Redis with a TTL (e.g., 1 hour)
    redis_client.set('cached_data', data, ex=3600)

    return data

if __name__ == '__main__':
    app.run(debug=True)
