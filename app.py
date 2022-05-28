#from atexit import register
#from crypt import methods
from enum import unique
import sys
import os
import re
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from send_mail import send_mail
import logging
import psycopg2 #pip install psycopg2 
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)


app.secret_key = 'irelandcoders-libertycrown'
 
DB_HOST = "localhost"
DB_NAME = "ratings_db"
DB_USER = "postgres"
DB_PASS = "PGBros*247#"
 
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    # postgre database connector
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:PGBros*247#@localhost/ratings_db'
else:
    #app.debug = False
    app.debug = True
    ALLOWED_HOSTS = [".school-teacher-feedbacks.herokuapp.com"]
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sedivizhluecdn:bb0656033ee97b12b724230e4d05120e9895c22b2519f881a3c8ddc646d372c2@ec2-3-230-122-20.compute-1.amazonaws.com:5432/d1foofbo9l0vgd'

app.config['SQLAlchemy_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, unique=False)
    selected_subject = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    def __init__(self,student_id, selected_subject,rating,comments):
        self.student_id = student_id
        self.selected_subject = selected_subject
        self.rating = rating
        self.comments = comments

@app.route('/')
def home_fx():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Check if user is loggedin
    if 'loggedin' in session:   
        # User is loggedin show them the home page
        #return render_template('home_pg.html', username=session['username'])
        cursor.execute('select fname from student_user where username = %s', (session['username'] ,))
        fn = cursor.fetchone()
        return render_template('home_pg.html', fname =fn[0].capitalize() )
    # User is not loggedin redirect to login page
    return redirect(url_for('login_fx'))
    

@app.route('/register_fx', methods = ['GET', 'POST'])
def register_fx():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'fname' in request.form and 'lname' in request.form and 'email' in request.form and 'registered_class' in request.form and 'passwd' in request.form and 'confirm_passwd' in request.form:
        # Create variables for easy access
        fname = request.form['fname']
        lname = request.form['lname']
        username = fname + '.' + lname
        email = request.form['email']
        registered_class = request.form['registered_class']
        passwd = request.form['passwd']
        confirm_passwd  = request.form['confirm_passwd']
    
        _hashed_passwd = generate_password_hash(passwd)
        _hashed_confirm_passwd = generate_password_hash(confirm_passwd)
 
        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM student_user WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', fname):
            flash('First Name must contain only characters and numbers!')
        elif not re.match(r'[A-Za-z0-9]+', lname):
            flash('Last Name must contain only characters and numbers!')
        elif not fname or not lname or not email or not registered_class or not passwd or not confirm_passwd :   
            flash('Please fill out all the fields!')
        #elif _hashed_passwd != _hashed_confirm_passwd:
        elif passwd != confirm_passwd:
            flash('Passwords not the same!')              
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            #cursor.execute("INSERT INTO student_user (fname, lname, username, passwd, email) VALUES (%s,%s,%s,%s,%s)", (fname,lname, username, _hashed_passwd, email))
            cursor.execute("INSERT INTO student_user (fname, lname, username, email, registered_class, passwd, confirm_passwd) VALUES (%s,%s,%s,%s,%s,%s,%s)", (fname, lname, username, email, registered_class, _hashed_passwd, _hashed_confirm_passwd))
            conn.commit()
            flash('Registration successful!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register_pg.html')


@app.route('/login_fx/', methods=['GET', 'POST'])
def login_fx():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'passwd' in request.form:
        username = request.form['username']
        passwd = request.form['passwd']
        print(passwd)
 
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM student_user WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
 
        if account:
            password_rs = account['passwd']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, passwd):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home_fx'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')
 
    return render_template('login_pg.html')

@app.route('/logout_fx')
def logout_fx():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login_fx'))
  
@app.route('/profile_fx')
def profile_fx(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM student_user WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile_pg.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login_fx'))    
 
@app.route('/feedback_fx')
def feedback_fx():
    return render_template('home_pg.html')

@app.route('/submit', methods =['POST'])
def submit():
    if request.method == 'POST':
        #student_id = request.form['student_id']
        #selected_subject = request.form['selected_subject']
        student_users_id = request.form['student_users_id']
        subject_name = request.form['subject_name']
        topic_name = request.form['topic_name'] 
        rating = request.form['rating'] 
        comments = request.form['comments'] 
  
        if student_users_id == '' or subject_name  == '':
            return render_template('home_pg.html', message = 'Please enter all required fields!')
        if db.session.query(Feedback).filter(Feedback.topic_id == topic_name).count()== 0:
            data = Feedback(student_users_id, subject_name, topic_name,rating,comments)
            db.session.add(data)
            db.session.commit()
            send_mail(student_users_id, subject_name, topic_name, rating,comments)   
            return render_template('success.html')
        return render_template('home_pg.html', message = 'You have already submitted your feedback')     

if __name__ == '__main__':
    app.debug = True
    app.run()

uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)