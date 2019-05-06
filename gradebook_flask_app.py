
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["DEBUG"] = True


SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="andrewaustin",
    password="gradebook",
    hostname="andrewaustin.mysql.pythonanywhere-services.com",
    databasename="andrewaustin$gradebook",
)


app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Student(db.Model):
    __tablename__ = "student"

    studentId = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(4096))
    lastName = db.Column(db.String(4096))
    studentMajor = db.Column(db.String(4096))
    studentEmail = db.Column(db.String(4096))

class Assignment(db.Model):
    __tablename__= "assignment"

    assignmentId = db.Column(db.Integer, primary_key=True)
    assignmentName = db.Column(db.String(4096))

class Grade(db.Model):
    __tablename__= "grade"

    gradeId = db.Column(db.Integer, primary_key=True)
    studentId = db.Column(db.Integer, db.ForeignKey('student.studentId'),nullable=True)
    assignmentId = db.Column(db.Integer, db.ForeignKey('assignment.assignmentId'),nullable=True)
    grade = db.Column(db.Integer)



@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/login')
def login():
    return 'login here.'

#andrew
@app.route('/roster')
def roster():
    return render_template('roster.html')

#andrew
@app.route('/edit_grades')
def editGrades():
    return 'Edit grades'

#andrew
@app.route("/add_delete_student", methods=["GET", "POST"])
def addDeleteStudent():
    if request.method == 'GET':
        return render_template("add_delete_student.html", students=Student.query.all())

    if request.form["addDelRad"] == "add":
        student = Student(firstName=request.form["fNameInput"], lastName=request.form["lNameInput"], studentMajor=request.form["majorInput"], studentEmail=request.form["emailInput"])
        db.session.add(student)
        db.session.commit()
    else:
        delStudId = request.form["delStudId"]
        delStudfName = request.form["fNameInput"]
        delStudlName = request.form["lNameInput"]
        delStudMaj = request.form["majorInput"]
        delStudEmail = request.form["emailInput"]
        deleteStudent = Student.query.filter_by(studentId=delStudId, firstName=delStudfName, lastName=delStudlName, studentMajor=delStudMaj, studentEmail=delStudEmail).first()
        if deleteStudent is not None:
            db.session.delete(deleteStudent)
            db.session.commit()
        else:
            noUser = True
            return render_template('add_delete_student.html', noUser=noUser, students=Student.query.all())

    return redirect(url_for('addDeleteStudent'))
