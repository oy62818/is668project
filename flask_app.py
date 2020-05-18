from flask import Flask, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash


app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="is668project1",
    password="returnvo!D1",
    hostname="is668project1.mysql.pythonanywhere-services.com",
    databasename="is668project1$gradebook",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.secret_key = "RezwanBryanIs668"
login_manager = LoginManager()
login_manager.init_app(app)

class users(UserMixin, db.Model):
    __tablename__ = 'users'
    userid = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(100))
    major = db.Column(db.String(100))
    password_hash = db.Column(db.String(128))
    isactive = db.Column(db.Boolean)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def get_id(self):
        return self.firstname

@login_manager.user_loader
def load_user(username):
    return users.query.filter_by(firstname=username).first()

class assignments(db.Model):
    __tablename__ = 'assignments'
    assignmentid = db.Column(db.Integer, primary_key=True)
    assignmenttitle = db.Column(db.String(200))
    maxpoints = db.Column(db.Integer)

class grades(db.Model):
    __tablename__ = 'grades'
    gradeid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey(users.userid))
    assignmentid = db.Column(db.Integer, db.ForeignKey(assignments.assignmentid))
    grade = db.Column(db.Integer)

# calculate overall GPA for each student
#def gpa(db.model):
#    stotal


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=False)

    user = load_user(request.form["userid"])
    if user is None:
        return render_template("login.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("login.html", error=True)

    login_user(user)
    return redirect(url_for('home'))


#This is when the user logged in to display welcome page
@app.route("/is668/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("home.html")

    if not current_user.is_authenticated:
        return redirect(url_for('login'))


# This is the page with student roster
@app.route("/is668/student/", methods=["GET", "POST"])
def student():
    if request.method == "GET":
        return render_template("studentlist.html", student=users.query.all())

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

#******** View Student Info*******######
@app.route("/is668/student/detail/", methods=["GET", "POST"])
def studentdetail():
    student_id=request.form.get("currentid")
    currentstudent = users.query.filter_by(userid=student_id).first()
    return render_template("studentdetail.html", student = currentstudent, grades=grades.query.all(), assignments=assignments.query.all())


    if not current_user.is_authenticated:
        return redirect(url_for('login'))


# This is the page to add or delete student
@app.route("/is668/student/enroll/", methods=["GET", "POST"])
def enroll():
    if request.method == "GET":
        return render_template("enroll.html", student=users.query.all())

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

#******** Update enrollment*******######
@app.route("/is668/student/enroll/updatestudent", methods=["POST"])
def updatestudent():
    student_id = request.form.get("currentid")
    changestudent = users.query.filter_by(userid=student_id).first()

    if(changestudent.isactive == True):
        changestudent.isactive = False
    else:
        changestudent.isactive = True
    db.session.commit()
    return redirect(url_for('enroll'))

# This is the page with assignments
@app.route("/is668/assignment/", methods=["GET", "POST"])
def assignment():
    if request.method == "GET":
        return render_template("assignment.html", assignments=assignments.query.all())

    if not current_user.is_authenticated:
        return redirect(url_for('login'))


# This is the page with grade
@app.route("/is668/grade/", methods=["GET", "POST"])
def grade():
    if request.method == "GET":
        return render_template("grade.html", grades=grades.query.all())

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

#******** Update new grade*******######
@app.route("/is668/grade/updategrade", methods=["POST"])
def updategrade():
    grade_id = request.form.get("currentid")
    newgrade = request.form.get("newgrade")
    changegrade = grades.query.filter_by(gradeid=grade_id).first()
    changegrade.grade = newgrade
    db.session.commit()
    return redirect(url_for('grade'))

#******** Add new assignments*******######

@app.route("/is668/assignment/new/", methods=["GET", "POST"])
def newassignment():
    if request.method == "GET":
        return render_template("newassignment.html")

    newassignment = assignments(assignmenttitle=request.form["assignmenttitle"], maxpoints=request.form["maxpoints"])
    db.session.add(newassignment)
    db.session.commit()
    return redirect(url_for('assignment'))

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

#******** Delete assignments*******######

@app.route("/is668/assignment/delete", methods=["GET", "POST"])
def deleteassignment():
    assignment_id = request.form.get("currentid")
    deletetask = assignments.query.filter_by(assignmentid=assignment_id).first()
    db.session.delete(deletetask)
    db.session.commit()
    return redirect(url_for('assignment'))

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
