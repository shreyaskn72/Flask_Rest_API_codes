from flask import Flask, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)


class YourTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Create tables
db.create_all()


@app.route('/create_row/<name>')
def create_row(name):
    new_row = YourTable(name=name)
    db.session.add(new_row)
    db.session.commit()

    return jsonify({'success': 'Row created successfully'}), 201


@app.route('/download_table/<primary_key>')
def download_table(primary_key):
    row = YourTable.query.get(primary_key)
    if not row:
        return jsonify({'error': 'Primary key not found'}), 404

    rows = YourTable.query.all()

    with open('YourTable.csv', 'w') as f:
        for row in rows:
            f.write(','.join(str(val) for val in row.to_dict().values()) + '\n')

    return send_file('YourTable.csv', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
