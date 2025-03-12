from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# Define the Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    year_of_admission = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile_picture = db.Column(db.String(100), nullable=False)

# Define the Lecturer model
class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lecturer_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile_picture = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

# Define the Course model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    units = db.relationship('Unit', backref='course', lazy=True)
    lecturers = db.relationship('Lecturer', backref='course', lazy=True)

# Define the Unit model
class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_name = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

# Define the StudentCourse model
class StudentCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

# Define the Assignment model
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(100), nullable=False)

# Define the LecturerAttendance model
class LecturerAttendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)

# Define the StudentAttendance model
class StudentAttendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

    class Grade(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
        unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
        grade = db.Column(db.String(10), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def main_login():
    return render_template('main_login.html')

@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        student_id = request.form['student-id']
        password = request.form['password']

        student = Student.query.filter_by(student_id=student_id, password=password).first()

        if student:
            session['student_id'] = student.student_id
            session['full_name'] = student.full_name
            session['profile_picture'] = student.profile_picture
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid student ID or password', 'danger')
            return redirect(url_for('student_login'))
    return render_template('Student_login.html')

@app.route('/lecturer_login', methods=['GET', 'POST'])
def lecturer_login():
    if request.method == 'POST':
        lecturer_id = request.form['lecturer-id']
        password = request.form['password']

        lecturer = Lecturer.query.filter_by(lecturer_id=lecturer_id, password=password).first()

        if lecturer:
            session['lecturer_id'] = lecturer.lecturer_id
            session['full_name'] = lecturer.full_name
            session['profile_picture'] = lecturer.profile_picture
            flash('Login successful!', 'success')
            return redirect(url_for('lecturer_dashboard'))
        else:
            flash('Invalid lecturer ID or password', 'danger')
            return redirect(url_for('lecturer_login'))
    return render_template('lecturer_login.html')

@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        student_id = request.form['student-id']
        full_name = request.form['full-name']
        email = request.form['email']
        age = request.form['age']
        year_of_admission = request.form['year-of-admission']
        password = request.form['password']
        profile_picture = request.files['profile-picture']

        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_picture_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            new_student = Student(student_id=student_id, full_name=full_name, email=email, age=age, year_of_admission=year_of_admission, password=password, profile_picture=profile_picture_url)
            db.session.add(new_student)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('student_login'))
    return render_template('student_register.html')

@app.route('/lecturer_register', methods=['GET', 'POST'])
def lecturer_register():
    if request.method == 'POST':
        lecturer_id = request.form['lecturer-id']
        full_name = request.form['full-name']
        email = request.form['email']
        password = request.form['password']
        course_id = request.form['course-id']
        profile_picture = request.files['profile-picture']

        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_picture_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            new_lecturer = Lecturer(lecturer_id=lecturer_id, full_name=full_name, email=email, password=password, course_id=course_id, profile_picture=profile_picture_url)
            db.session.add(new_lecturer)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('lecturer_login'))
    return render_template('lecturer_register.html')

@app.route('/dashboard')
def dashboard():
    if 'student_id' in session:
        student_id = session['student_id']
        full_name = session['full_name']
        profile_picture = session['profile_picture']
        student = Student.query.filter_by(student_id=student_id).first()
        student_courses = StudentCourse.query.filter_by(student_id=student.id).all()
        courses = [Course.query.get(sc.course_id) for sc in student_courses]
        all_courses = Course.query.all()
        return render_template('dashboard.html', student_id=student_id, full_name=full_name, profile_picture=profile_picture, courses=courses, all_courses=all_courses)
    else:
        flash('Please login first.', 'danger')
        return redirect(url_for('student_login'))

@app.route('/lecturer_dashboard')
def lecturer_dashboard():
    if 'lecturer_id' in session:
        full_name = session['full_name']
        profile_picture = session['profile_picture']
        lecturer_id = session['lecturer_id']
        lecturer = Lecturer.query.filter_by(lecturer_id=lecturer_id).first()
        units = Unit.query.filter_by(course_id=lecturer.course_id).all()
        return render_template('lecturer_dashboard.html', full_name=full_name, profile_picture=profile_picture, units=units)
    else:
        flash('Please login first.', 'danger')
        return redirect(url_for('lecturer_login'))
@app.route('/attendance_progress')
def attendance_progress():
    if 'lecturer_id' in session:
        full_name = session['full_name']
        profile_picture = session['profile_picture']
        lecturer_id = session['lecturer_id']
        lecturer = Lecturer.query.filter_by(lecturer_id=lecturer_id).first()

        # Track lecturer visit
        today = datetime.utcnow().date()
        if not LecturerAttendance.query.filter_by(lecturer_id=lecturer.id, date=today).first():
            new_attendance = LecturerAttendance(lecturer_id=lecturer.id, date=today)
            db.session.add(new_attendance)
            db.session.commit()

        # Get timetable data
        timetable = [
            {'name': 'Monday', 'visited': LecturerAttendance.query.filter_by(lecturer_id=lecturer.id, date=today).first() is not None},
            {'name': 'Tuesday', 'visited': LecturerAttendance.query.filter_by(lecturer_id=lecturer.id, date=today).first() is not None},
            {'name': 'Wednesday', 'visited': LecturerAttendance.query.filter_by(lecturer_id=lecturer.id, date=today).first() is not None},
            {'name': 'Thursday', 'visited': LecturerAttendance.query.filter_by(lecturer_id=lecturer.id, date=today).first() is not None},
            {'name': 'Friday', 'visited': LecturerAttendance.query.filter_by(lecturer_id=lecturer.id, date=today).first() is not None},
            {'name': 'Saturday', 'visited': LecturerAttendance.query.filter_by(lecturer_id=lecturer.id, date=today).first() is not None},
            {'name': 'Sunday', 'visited': LecturerAttendance.query.filter_by(lecturer_id=lecturer.id, date=today).first() is not None},
        ]

        # Get students visited today
        students_visited_today = StudentAttendance.query.filter_by(date=today).all()
        total_students_visited_today = len(students_visited_today)
        students_visited_today = [Student.query.get(sa.student_id) for sa in students_visited_today]

        return render_template('attendance_progress.html', full_name=full_name, profile_picture=profile_picture, timetable=timetable, students_visited_today=students_visited_today, total_students_visited_today=total_students_visited_today)
    else:
        flash('Please login first.', 'danger')
        return redirect(url_for('lecturer_login'))

@app.route('/input_grades', methods=['GET', 'POST'])
def input_grades():
    if 'lecturer_id' in session:
        if request.method == 'POST':
            student_id = request.form['student-id']
            unit_id = request.form['unit-id']
            grade = request.form['grade']

            new_grade = Grade(student_id=student_id, unit_id=unit_id, grade=grade)
            db.session.add(new_grade)
            db.session.commit()
            flash('Grade submitted successfully!', 'success')
            return redirect(url_for('input_grades'))

        full_name = session['full_name']
        profile_picture = session['profile_picture']
        return render_template('input_grades.html', full_name=full_name, profile_picture=profile_picture)
    else:
        flash('Please login first.', 'danger')
        return redirect(url_for('lecturer_login'))

@app.route('/register_course/<int:course_id>')
def register_course(course_id):
    if 'student_id' in session:
        student_id = session['student_id']
        student = Student.query.filter_by(student_id=student_id).first()
        new_student_course = StudentCourse(student_id=student.id, course_id=course_id)
        db.session.add(new_student_course)
        db.session.commit()
        flash('Course registered successfully!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Please login first.', 'danger')
        return redirect(url_for('student_login'))

@app.route('/unit_registration')
def unit_registration():
    if 'student_id' in session:
        student_id = session['student_id']
        student = Student.query.filter_by(student_id=student_id).first()
        student_courses = StudentCourse.query.filter_by(student_id=student.id).all()
        courses = [Course.query.get(sc.course_id) for sc in student_courses]
        units = [unit for course in courses for unit in course.units]
        return render_template('unit_registration.html', units=units, full_name=student.full_name, profile_picture=student.profile_picture)
    else:
        flash('Please login first.', 'danger')
        return redirect(url_for('student_login'))

@app.route('/register_units', methods=['POST'])
def register_units():
    if 'student_id' in session:
        student_id = session['student_id']
        student = Student.query.filter_by(student_id=student_id).first()
        selected_units = request.form.getlist('units')
        for unit_id in selected_units:
            unit = Unit.query.get(unit_id)
            # Add logic to register the unit for the student
            # For example, you might want to create a new StudentUnit model to track this
        flash('Units registered successfully!', 'success')
        return redirect(url_for('unit_registration'))
    else:
        flash('Please login first.', 'danger')
        return redirect(url_for('student_login'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        student_id = request.form['student-id']
        new_password = request.form['new-password']

        student = Student.query.filter_by(student_id=student_id).first()
        if student:
            student.password = new_password
            db.session.commit()
            flash('Password reset successful! Please login with your new password.', 'success')
        else:
            flash('Student ID not found.', 'danger')
        return redirect(url_for('student_login'))
    return render_template('reset_password.html')

@app.route('/lecturer_register_unit', methods=['GET', 'POST'])
def lecturer_register_unit():
    if request.method == 'POST':
        unit_name = request.form['unit-name']
        course_id = request.form['course-id']

        new_unit = Unit(unit_name=unit_name, course_id=course_id)
        db.session.add(new_unit)
        db.session.commit()
        flash('Unit registered successfully!', 'success')
        return redirect(url_for('lecturer_dashboard'))
    return render_template('lecturer_register_unit.html')

@app.route('/lecturer_post_assignment', methods=['GET', 'POST'])
def lecturer_post_assignment():
    if request.method == 'POST':
        unit_id = request.form['unit-id']
        assignment_title = request.form['assignment-title']
        assignment_file = request.files['assignment-file']

        if assignment_file:
            filename = secure_filename(assignment_file.filename)
            assignment_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            new_assignment = Assignment(unit_id=unit_id, title=assignment_title, file_path=file_path)
            db.session.add(new_assignment)
            db.session.commit()
            flash('Assignment posted successfully!', 'success')
            return redirect(url_for('lecturer_dashboard'))
    return render_template('lecturer_post_assignment.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main_login'))

if __name__ == '__main__':
    app.run(debug=True)