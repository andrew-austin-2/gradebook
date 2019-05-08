
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
from flask_login import login_required, login_user, LoginManager, logout_user, UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash
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

app.secret_key = "andrewandaustinarecool"
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

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


#austin
@app.route('/', methods=["GET", "POST"])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("main_page.html")
    return redirect(url_for('index'))

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    user = load_user(request.form["username"])
    if user is None:
        return render_template("login_page.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    login_user(user)
    return redirect(url_for('index'))

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#andrew
@app.route('/roster', methods=["GET", "POST"])
def roster():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
        # grades will be ordered by the assignmentID so that no matter what order the assignments the students have are created in, it will be in the right order
        return render_template("roster.html", students=Student.query.all(), grades=Grade.query.order_by(Grade.assignmentId).all(), assignments=Assignment.query.all())

#andrew
@app.route('/edit_grades', methods=["GET", "POST"])
def editGrades():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template("edit_grades.html", students=Student.query.all(), grades=Grade.query.all(), assignments=Assignment.query.all())
    #can probably get rid of the first and last names. user can verify with the table below for the correct student based on the id
    studID = request.form["studID"]
    assignmentName = request.form["assignmentName"]
    gradeReceived = request.form["assignmentGrade"]

    #search to get the assignment ID
    assignmentID = Assignment.query.filter_by(assignmentName=assignmentName).first()
    assignmentID = assignmentID.assignmentId
    #Assignment action must be done first. Check to see if it exists for that student.

    gradeToChange = Grade.query.filter_by(studentId=studID, assignmentId=assignmentID, grade=gradeReceived).first() # checks to see if we need to add a grade or just update.

    if gradeToChange is None:
        #add/update new grade to grade table
        updateOrAdd = Grade.query.filter_by(studentId=studID, assignmentId=assignmentID).first() # if it returns something (not None)... then update table, if not (None), add to table
        changeGrade = Grade(studentId=studID, assignmentId=assignmentID, grade=gradeReceived)
        if updateOrAdd is None:
            db.session.add(changeGrade)
            db.session.commit()
        else:
            updateOrAdd.grade = gradeReceived
            db.session.commit()
    else:
        #there was already a grade for that assignment and user with the same grade.
        gradeToChange = False
        return render_template('edit_grades.html', gradeToChange=gradeToChange, students=Student.query.all(), grades=Grade.query.all(), assignments=Assignment.query.all())

    return redirect(url_for('editGrades'))

#andrew
@app.route("/add_delete_student", methods=["GET", "POST"])
def addDeleteStudent():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    action = 0
    if request.method == 'GET':
        return render_template("add_delete_student.html", students=Student.query.all(), grades=Grade.query.all(), assignments=Assignment.query.all())

    if request.form["addDelRad"] == "add":
        student = Student(firstName=request.form["fNameInput"], lastName=request.form["lNameInput"], studentMajor=request.form["majorInput"], studentEmail=request.form["emailInput"])
        db.session.add(student)
        db.session.commit()
        action = 1 # action = 1 if you successfully add a user.
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

    return render_template('add_delete_student.html', action=action)
