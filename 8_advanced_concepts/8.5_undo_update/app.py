from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(100))

class OriginalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'))
    original_data = db.Column(db.String(100))
    entry = db.relationship('Entry', backref='original_entry')

# API to create a row in the database
@app.route('/create_entry', methods=['POST'])
def create_entry():
    data = request.json.get('data')
    new_entry = Entry(data=data)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({'message': 'Entry created successfully'}), 201

# API to update a row in the database
@app.route('/update_entry/<int:entry_id>', methods=['PUT'])
def update_entry(entry_id):
    entry = Entry.query.get(entry_id)
    if not entry:
        return jsonify({'message': 'Entry not found'}), 404
    new_data = request.json.get('data')
    # Save the original data before updating
    original_entry = OriginalEntry(entry_id=entry.id, original_data=entry.data)
    db.session.add(original_entry)
    entry.data = new_data
    db.session.commit()
    return jsonify({'message': 'Entry updated successfully'}), 200

# API to undo the update and bring back original entries
@app.route('/undo_update/<int:entry_id>', methods=['PUT'])
def undo_update(entry_id):
    entry = Entry.query.get(entry_id)
    if not entry:
        return jsonify({'message': 'Entry not found'}), 404
    # Retrieve the original data and restore it
    original_entry = OriginalEntry.query.filter_by(entry_id=entry.id).first()
    if original_entry:
        entry.data = original_entry.original_data
        db.session.delete(original_entry)
        db.session.commit()
        return jsonify({'message': 'Update undone successfully'}), 200
    else:
        return jsonify({'message': 'No original data available to restore'}), 400

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
