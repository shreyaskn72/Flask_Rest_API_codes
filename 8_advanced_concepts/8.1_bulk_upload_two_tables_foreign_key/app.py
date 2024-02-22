from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///primary_foreign.db'
db = SQLAlchemy(app)

class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    children = db.relationship('Child', backref='parent', lazy=True)

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)

@app.route('/upload', methods=['POST'])
def upload_data():
    data = request.json
    parents_data = data.get('parents', [])

    try:
        parents = [Parent(name=parent['name']) for parent in parents_data]
        db.session.add_all(parents)
        db.session.flush()

        parent_ids = [parent.id for parent in parents]

        #children = [Child(name=child['name'], parent_id=parent_ids[i]) for i, child in enumerate(children_data)]
        children = [Child(name="notes_fine", parent_id=i) for i in parent_ids]
        db.session.add_all(children)
        db.session.commit()

        return jsonify({'message': 'Data uploaded successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)


"""



curl command
curl --location 'http://localhost:5000/upload' \
--header 'Content-Type: application/json' \
--data '{
    "parents": [
        {"name": "Parent 1"},
        {"name": "Parent 2"},
        {"name": "Parent 3"},
        {"name": "Parent 4"}
    ]
}'

"""