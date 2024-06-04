from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SECRET_KEY = 'YOUR_SECRET_KEY_HERE'
RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

def validate_recaptcha(token):
    data = {
        'secret': SECRET_KEY,
        'response': token
    }
    response = requests.post(RECAPTCHA_VERIFY_URL, data=data)
    result = response.json()
    return result['success']

@app.route('/validate-recaptcha', methods=['POST'])
def validate_recaptcha_api():
    token = request.json.get('token')
    if token:
        if validate_recaptcha(token):
            return jsonify({'success': True, 'message': 'reCAPTCHA validation successful'})
        else:
            return jsonify({'success': False, 'message': 'reCAPTCHA validation failed'})
    else:
        return jsonify({'success': False, 'message': 'No token provided'})

if __name__ == '__main__':
    app.run(debug=True)
