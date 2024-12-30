from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
from markupsafe import escape  # Import escape untuk sanitasi data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

    # Sanitasi data yang diambil sebelum diteruskan ke template
    sanitized_students = [
        {
            'id': student[0],
            'name': escape(student[1]),
            'age': student[2],
            'grade': escape(student[3])
        }
        for student in students
    ]

    # Mengembalikan data ke template dengan data yang sudah disanitasi
    return render_template('index.html', students=sanitized_students)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']

    #tidak menggunakan koneksi secara manual karen sudah pakai Flask-SQLAlchemy dan hanya perlu pakai db.session.commit().
    query = text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)")
    db.session.execute(query, {'name': name, 'age': age, 'grade': grade})
    db.session.commit()

    return redirect(url_for('index'))

    

    #connection = sqlite3.connect('instance/students.db')
    #cursor = connection.cursor()

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()

    #query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    #cursor.execute(query)
    #connection.commit()
    #connection.close()
    #return redirect(url_for('index'))




@app.route('/delete/<string:id>') 
def delete_student(id):
    # RAW Query
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if request.method == 'POST':
        # Mengambil data dari form
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        # Query untuk memperbarui data student
        query = text("UPDATE student SET name = :name, age = :age, grade = :grade WHERE id = :id")
        db.session.execute(query, {'name': name, 'age': age, 'grade': grade, 'id': id})
        db.session.commit()

        # Redirect ke halaman utama setelah berhasil update
        return redirect(url_for('index'))
    else:
        # Query untuk mengambil data student berdasarkan ID
        query = text("SELECT * FROM student WHERE id = :id")
        student = db.session.execute(query, {'id': id}).fetchone()

        # Render template untuk halaman edit
        return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

