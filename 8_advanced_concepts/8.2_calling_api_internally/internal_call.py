from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/hello', methods=['POST'])
def hello():
    data = request.json
    name = data.get('Name')
    greeting_message = 'Hello! ' + str(name)
    greeting_dict = {"greeting": greeting_message}
    return greeting_dict

@app.route('/internal_call', methods=['POST'])
def index():
    # Internal call to the Flask API with a payload
    payload = request.json

    city = payload.get('City')

    with app.test_client() as c:
        # Make an internal request to the '/api/endpoint' endpoint with the payload
        response = c.post('/hello', json=payload)

        # Extract data from the response
        response_data = response.get_json()

    second_response = {"second_response": f"hopefully you will enjoy in {city}"}
    response_data.update(second_response)


    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
