from flask import Flask, render_template, request, redirect, url_for, flash
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from flask import request, jsonify

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {"timeout": 15}
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

# ------------------- CONTACT FORM MODEL -------------------
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    message = db.Column(db.Text)

# ------------------- USER MODEL -------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150))
    score = db.Column(db.Integer, default=0)

# ------------------- FORMS -------------------
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=30)])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=30)])
    submit = SubmitField('Register')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = StringField('Message', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Send Message')

# ------------------- SAVE SCORE -------------------

@app.route('/save_score', methods=['POST'])
def save_score():

    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    score = data['score']

    user = User.query.get(session['user'])

    user.score = score
    db.session.commit()

    return jsonify({"message": "Score saved"})

# ------------------- HOME PAGE -------------------
@app.route('/')
def home():
    return render_template('index.html')

# ------------------- REGISTER -------------------
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # check if user already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("User already exists. Please login.")
            return redirect(url_for('login'))

        # hash password
        hashed_password = generate_password_hash(password)

        # create user
        new_user = User(fullname=name, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.")
        return redirect(url_for('login'))

    return render_template("login.html")

# ------------------- LOGIN -------------------
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.id
            flash("Login successful!")
            return redirect(url_for('mainpage'))
        else:
            flash("Invalid email or password")

    return render_template("login.html")

# ------------------- MAIN PAGE -------------------

@app.route('/mainpage')
def mainpage():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('quiz.html')

# ------------------- ABOUT -------------------
@app.route('/about')
def about():
    return redirect(url_for('home')+ '#about')
# ------------------- CONTACT -------------------
# ------------------- CONTACT -------------------
@app.route('/contact', methods=['POST'])
def contact():

    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    new_message = Contact(name=name, email=email, message=message)

    db.session.add(new_message)
    db.session.commit()

    flash("Thank you for contacting us!")

    return redirect(url_for('home') + "#contact")

# ------------------- CREATE DATABASE -------------------
with app.app_context():
    db.create_all()


# ------------------- RUN APP -------------------
if __name__ == '__main__':
    app.run(debug=True)