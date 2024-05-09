from flask import Flask,render_template,request,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from sqlalchemy import text

#my db connection
local_server=True

app = Flask(__name__)
app.secret_key = 'key'

login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(get_id):
    return User.query.get(int(get_id))

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/hmssk'
db = SQLAlchemy(app)

class User(UserMixin,db.Model):
    uid=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(50))
    def get_id(self):
        return str(self.uid)

class Students(db.Model):
    sid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50),unique=True)
    name=db.Column(db.String(50))
    hostel=db.Column(db.String(50))
    number=db.Column(db.String(12))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student',methods=['POST','GET'])
@login_required
def student():
    doct=db.session.execute(text("SELECT * FROM `user`"))
    print(doct)
    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        hostel=request.form.get('hostel')
        number=request.form.get('number')
        new_student = Students(email=email, name=name, hostel=hostel, number=number)
        db.session.add(new_student)
        db.session.commit()
        # try:
        #     db.session.commit()
        #     return redirect(url_for('index'))
        # except Exception as e:
        #     db.session.rollback()
    return render_template('student.html',doct=doct)

@app.route('/details')
@login_required
def details():
    em=current_user.email
    query=db.session.execute(text(f"SELECT * FROM `students` WHERE email='{em}'"))
    return render_template('details.html',query=query)

@app.route("/edit/<int:sid>", methods=['POST', 'GET'])
@login_required
def edit(sid):
    student = Students.query.get(sid)
    if request.method == "POST":
        student.email = request.form.get('email')
        student.name = request.form.get('name')
        student.hostel = request.form.get('hostel')
        student.number = request.form.get('number')
        db.session.commit()
        return redirect('/details')
        ## try:
        #     db.session.commit()
        #     return redirect('/details')
        # except Exception as e:
        #     db.session.rollback()
        #     return redirect(url_for('edit', sid=sid))
    return render_template('edit.html', student=student)


@app.route("/delete/<string:sid>",methods=['POST','GET'])
@login_required
def delete(sid):
    db.session.execute(text(f"DELETE FROM students WHERE students.sid={sid}"))
    db.session.commit()
    return redirect('/details')

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
       username=request.form.get('username')
       email=request.form.get('email')
       password=request.form.get('password')
       user=User.query.filter_by(email=email).first()
       if user:
            return render_template('signup.html')

       new_user = User(username=username, email=email, password=password)
       db.session.add(new_user)
       db.session.commit()
       return render_template('login.html')
    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
       
       email=request.form.get('email')
       password=request.form.get('password')
       user=User.query.filter_by(email=email).first()
       if user:
        login_user(user)
        return redirect(url_for('index'))
       else:
        return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

app.run(debug=True)
