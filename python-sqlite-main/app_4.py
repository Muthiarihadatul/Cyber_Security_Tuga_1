from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey' 
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

@app.route('/')
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

# Input validation function
def validate_input(name, age, grade):
    # Validate name: ama hanya boleh mengandung huruf dan spasi
    if not re.match(r'^[A-Za-z\s]+$', name):
        return False, "Nama hanya boleh mengandung huruf dan spasi."

    # Validate age: Usia harus berupa bilangan bulat positif
    if not age.isdigit() or int(age) <= 0:
        return False, "Usia harus berupa bilangan bulat positif."

    # Validate grade: Nilai harus berupa Huruf atau bilangan bulat positif
    if not re.match(r'^[A-Za-z]+$', grade) and not grade.isdigit():
        return False, "Nilai harus berupa Huruf atau bilangan bulat positif."

    return True, "Valid input."

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name'].strip()
    age = request.form['age'].strip()
    grade = request.form['grade'].strip()
    

    connection = sqlite3.connect('instance/students.db')
    cursor = connection.cursor()

    # Validate input in add_student
    valid, message = validate_input(name, age, grade)
    if not valid:
        flash(message)
        return redirect(url_for('index'))

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()
    query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    cursor.execute(query)
    connection.commit()
    connection.close()
    return redirect(url_for('index'))


@app.route('/delete/<string:id>') 
def delete_student(id):
    # RAW Query
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if request.method == 'POST':
        name = request.form['name'].strip()
        age = request.form['age'].strip()
        grade = request.form['grade'].strip()

        # Validate input in edit_student
        valid, message = validate_input(name, age, grade)
        if not valid:
            flash(message)
            return redirect(url_for('edit_student', id=id))
        
        # Update dengan parameterized query
        db.session.execute(
            text("UPDATE student SET name = :name, age = :age, grade = :grade WHERE id = :id"),
            {"name": name, "age": int(age), "grade": grade, "id": id}
        )
        db.session.commit()

        # Redirect kembali ke halaman index
        return redirect(url_for('index'))
    else:
        # Ambil data student berdasarkan ID untuk form edit
        student = db.session.execute(
            text("SELECT * FROM student WHERE id = :id"),
            {"id": id}
        ).fetchone()

        # Render halaman edit dengan data student
        return render_template('edit.html', student=student)


# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

    

