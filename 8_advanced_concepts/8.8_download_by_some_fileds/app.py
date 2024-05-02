from flask import Flask, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)


class YourTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    other_table = db.relationship('OtherTable', backref='your_table', lazy=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class OtherTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    your_table_id = db.Column(db.Integer, db.ForeignKey('your_table.id'), nullable=False)
    data = db.Column(db.String(100))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Create tables
db.create_all()


@app.route('/create_row/<name>/<age>')
def create_row(name, age):
    new_row = YourTable(name=name, age=age)
    db.session.add(new_row)

    db.session.commit()

    # Create multiple rows in OtherTable with foreign key to YourTable
    for i in range(3):  # Create 3 sample rows in OtherTable
        new_other_row = OtherTable(your_table_id=new_row.id, data=f"Sample Data {i + 1}")
        db.session.add(new_other_row)

    db.session.commit()

    return jsonify({'success': 'Rows created successfully'}), 201

@app.route('/create_other_extra_row/<primary_id>')
def create_extra_row(primary_id):

    # Create a row in OtherTable with foreign key to YourTable
    new_other_row = OtherTable(your_table_id=primary_id, data="Extra data")
    db.session.add(new_other_row)

    db.session.commit()

    return jsonify({'success': 'Rows created successfully'}), 201


@app.route('/download_tables_by_age/<int:age>')
def download_tables_by_age(age):
    your_table_rows = YourTable.query.filter_by(age=age).all()
    if not your_table_rows:
        return jsonify({'error': 'No data found for the given age'}), 404

    with open('tables_data_by_age.csv', 'w') as f:
        f.write('YourTable_id,YourTable_name,YourTable_age,OtherTable_id,OtherTable_data\n')
        for your_table_row in your_table_rows:
            other_table_rows = OtherTable.query.filter_by(your_table_id=your_table_row.id).all()
            for other_table_row in other_table_rows:
                f.write(
                    f"{your_table_row.id},{your_table_row.name},{your_table_row.age},{other_table_row.id},{other_table_row.data}\n")

    return send_file('tables_data_by_age.csv', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
