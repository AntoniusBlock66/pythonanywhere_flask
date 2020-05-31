from flask import Flask, render_template, redirect, request, url_for
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate

from datetime import datetime

#create app object from Flask class
app = Flask(__name__)
app.config["DEBUG"] = True

#db settings
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="antoniusblock",
    password="lineupsPW82",
    hostname="antoniusblock.mysql.pythonanywhere-services.com",
    databasename="antoniusblock$lineups",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#db model
db = SQLAlchemy(app)

#do I really need this if I am building from scratch ?? prolly not
#migrate = Migrate(app, db)

#set secret key and manage login
app.secret_key = "ldghlkdsfsfdlh"
login_manager = LoginManager()
login_manager.init_app(app)

##########class definitions#########
class User(UserMixin, db.Model):
    """
    Implementation of the user object, holding:
    user_id, username, and pw hash

    Linked to the 'users' table of the db
    """

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(132))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username

class Comment(db.Model):
    """
    Implementation of the comment object, which holds the contents
    of an input str to the input field of /test_tmpl/ endpoint.

    Linked to the 'comments' table of the db
    """

    __tablename__ = "comments"

    user_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4098))
    posted = db.Column(db.DateTime, default=datetime.now)
    commenter_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    commenter = db.relationship('User', foreign_keys=commenter_id)

class RequestInfo(db.Model):
    """
    Implementation of the object that holds information on
    any reuqest made to the API interface.

    Linked to the 'requests_log' table of the db
    """

    __tablename__ = "requests_log"

    user_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(4098))
    requested = db.Column(db.DateTime, default=datetime.now)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    requester = db.relationship('User', foreign_keys=requester_id)
############################################

#
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

#########add endpoints functionalities###########
#landing message on route
@app.route("/")
def index():
    return render_template("welcome_page.html")

@app.route("/comments/", methods=["GET", "POST"])
def show_comment_log():
    #confirm logged user
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == "GET":
        return render_template("comments_page.html", comments=Comment.query.all())

    #create the Python object that represents the comment
    #send comment to DB for storage (keeping transaction open)
    #commit DB query(/ies)
    comment = Comment(content=request.form["contents"], commenter=current_user)
    db.session.add(comment)
    db.session.commit()

    return redirect(url_for('show_comment_log'))

@app.route("/login/", methods=["GET", "POST"])
def login():
    #page was just opened
    if request.method == 'GET':
        return render_template("login_page.html", error=False)

    #load user from db
    user = load_user(request.form["username"])

    #user doesn't exist
    if user is None:
        return render_template("login_page.html", error=True)

    #user exists; checking password
    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    #succesful login
    login_user(user)

    return render_template("logged_in_msg.html")

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return render_template("logout_msg.html")

#launch
if __name__ == '__main__':
    app.run(debug=False)
    #app.run(host='0.0.0.0', port='5000')


#To initialise DB (one-off), from a python interpreter:
#$ ipython3.7
#In [1]: from lineups_main import db
#In [2]: db.create_all()


##To add users to the users db table:
##$export FLASK_APP=lineups_main.py
##$ flask shell
##>>> from lineups_main import db, User
##>>> from werkzeug.security import generate_password_hash #the password-hashing function
##admin = User(username="admin", password_hash=generate_password_hash("admin_pw"))
##db.session.add(admin)
##bob = User(username="bob", password_hash=generate_password_hash("bob_pw"))
##db.session.add(bob)
##db.session.commit()







