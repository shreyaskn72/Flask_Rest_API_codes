from flask import *
from flask import request

app = Flask(__name__)

@app.route("/add", methods=["POST"])

def json_example():
    if request.is_json:
      try:
        req = request.get_json()
        response_body = {
            "sum": req.get("number1")+req.get("number2")
        }
        res = make_response(jsonify(response_body), 200)
        return res
      except:
          res1 = make_response("number1 and number2 keys are required")
          return res1
    else:
        return make_response(jsonify({"message": "Request body must be JSON"}), 400)

if __name__ == '__main__':
    app.run(port=8080,debug=True)
