"""
Program illustrates to begin using flask for rest api development

"""

from flask import Flask

app = Flask(__name__)

@app.route('/')

def hello_world():
    return 'Hello, from Shreyas!'


if __name__== '__main__':
    app.run()
