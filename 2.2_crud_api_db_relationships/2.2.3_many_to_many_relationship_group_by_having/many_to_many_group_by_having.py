from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask app and the SQLAlchemy object
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students_courses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Association Table for Many-to-Many Relationship between Students and Courses
student_course = db.Table('student_course',
                          db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
                          db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
                          )


# Define the Student and Course models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    courses = db.relationship('Course', secondary=student_course, backref=db.backref('students', lazy='dynamic'))


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


# Initialize the database (you only need to run this once)
with app.app_context():
    db.create_all()


# API endpoint to demonstrate Many-to-Many JOIN (Get all students with their courses)
@app.route('/students_with_courses', methods=['GET'])
def get_students_with_courses():
    students_with_courses = db.session.query(
        Student.id.label('student_id'),
        Student.name.label('student_name'),
        Course.id.label('course_id'),
        Course.name.label('course_name')
    ).join(student_course, Student.id == student_course.c.student_id).join(Course,
                                                                           Course.id == student_course.c.course_id).all()

    result = []
    for row in students_with_courses:
        result.append({
            'student_id': row.student_id,
            'student_name': row.student_name,
            'course_id': row.course_id,
            'course_name': row.course_name
        })

    return jsonify(result)


# Create a new student
@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    if not data or not data.get('name'):
        abort(400, 'Student name is required')

    new_student = Student(name=data['name'])
    db.session.add(new_student)
    db.session.commit()
    return jsonify({'id': new_student.id, 'name': new_student.name}), 201


# Update an existing student
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get(id)
    if not student:
        abort(404, 'Student not found')

    data = request.get_json()
    if data.get('name'):
        student.name = data['name']

    db.session.commit()
    return jsonify({'id': student.id, 'name': student.name})


# Delete a student
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get(id)
    if not student:
        abort(404, 'Student not found')

    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'Student deleted successfully'})


# Create a new course
@app.route('/courses', methods=['POST'])
def create_course():
    data = request.get_json()
    if not data or not data.get('name'):
        abort(400, 'Course name is required')

    new_course = Course(name=data['name'])
    db.session.add(new_course)
    db.session.commit()
    return jsonify({'id': new_course.id, 'name': new_course.name}), 201


# Update an existing course
@app.route('/courses/<int:id>', methods=['PUT'])
def update_course(id):
    course = Course.query.get(id)
    if not course:
        abort(404, 'Course not found')

    data = request.get_json()
    if data.get('name'):
        course.name = data['name']

    db.session.commit()
    return jsonify({'id': course.id, 'name': course.name})


# Delete a course
@app.route('/courses/<int:id>', methods=['DELETE'])
def delete_course(id):
    course = Course.query.get(id)
    if not course:
        abort(404, 'Course not found')

    db.session.delete(course)
    db.session.commit()
    return jsonify({'message': 'Course deleted successfully'})


# API endpoint to enroll a student in a course (Many-to-Many)
@app.route('/students/<int:student_id>/courses/<int:course_id>', methods=['POST'])
def enroll_student_in_course(student_id, course_id):
    student = Student.query.get(student_id)
    course = Course.query.get(course_id)
    if not student or not course:
        abort(404, 'Student or Course not found')

    # Enroll student in the course (many-to-many relationship)
    if course not in student.courses:
        student.courses.append(course)
        db.session.commit()

    return jsonify({'student_id': student.id, 'student_name': student.name, 'course_id': course.id,
                    'course_name': course.name}), 200


# API endpoint to disenroll a student from a course (Many-to-Many)
@app.route('/students/<int:student_id>/courses/<int:course_id>', methods=['DELETE'])
def disenroll_student_from_course(student_id, course_id):
    student = Student.query.get(student_id)
    course = Course.query.get(course_id)
    if not student or not course:
        abort(404, 'Student or Course not found')

    # Disenroll student from the course
    if course in student.courses:
        student.courses.remove(course)
        db.session.commit()

    return jsonify({'message': 'Student disenrolled from course successfully'}), 200


# API endpoint to demonstrate GROUP BY (many-to-many)
@app.route('/courses_student_count', methods=['GET'])
def courses_student_count():
    result = db.session.query(
        Course.id.label('course_id'),
        Course.name.label('course_name'),
        db.func.count(student_course.c.student_id).label('student_count')
    ).join(student_course, Course.id == student_course.c.course_id).group_by(Course.id).all()

    courses_with_student_count = []
    for row in result:
        courses_with_student_count.append({
            'course_id': row.course_id,
            'course_name': row.course_name,
            'student_count': row.student_count
        })

    return jsonify(courses_with_student_count)


# API endpoint to demonstrate HAVING clause (many-to-many)
@app.route('/courses_student_count_having', methods=['GET'])
def courses_student_count_having():
    min_students = request.args.get('min_students', 1, type=int)

    result = db.session.query(
        Course.id.label('course_id'),
        Course.name.label('course_name'),
        db.func.count(student_course.c.student_id).label('student_count')
    ).join(student_course, Course.id == student_course.c.course_id).group_by(Course.id).having(
        db.func.count(student_course.c.student_id) >= min_students).all()

    courses_with_student_count = []
    for row in result:
        courses_with_student_count.append({
            'course_id': row.course_id,
            'course_name': row.course_name,
            'student_count': row.student_count
        })

    return jsonify(courses_with_student_count)


# API endpoint to demonstrate HAVING clause and list all students enrolled in a course (many-to-many)
@app.route('/courses_student_count_having_with_students', methods=['GET'])
def courses_student_count_having_with_students():
    min_students = request.args.get('min_students', 1, type=int)

    result = db.session.query(
        Course.id.label('course_id'),
        Course.name.label('course_name'),
        db.func.count(student_course.c.student_id).label('student_count'),
        db.func.group_concat(Student.name).label('student_names')  # Aggregate student names
    ).join(student_course, Course.id == student_course.c.course_id) \
     .join(Student, Student.id == student_course.c.student_id) \
     .group_by(Course.id) \
     .having(db.func.count(student_course.c.student_id) >= min_students) \
     .all()

    courses_with_students = []
    for row in result:
        courses_with_students.append({
            'course_id': row.course_id,
            'course_name': row.course_name,
            'student_count': row.student_count,
            'students': row.student_names.split(',')  # Convert comma-separated names into a list
        })

    return jsonify(courses_with_students)

if __name__ == '__main__':
    app.run(debug=True)