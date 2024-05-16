from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Users, BookRequest
from flask_bcrypt import check_password_hash
from Library import db, bcrypt,login_manager
from flask_login import login_user, login_required, logout_user
from Library import app
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

bp = Blueprint('user', __name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user)
                ct = datetime.now()
                books = BookRequest.query.filter_by(approved = True)
                for i in books:
                    if ct > i.date_return :
                        i.approved = False
                db.session.commit()
                return redirect("/userdb")
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')

    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        user = Users.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(username) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password != confirm:
            flash('Passwords don\'t match.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            hash_password = bcrypt.generate_password_hash(password).decode("utf-8")
            new_user = Users(email=email, username = username, password = hash_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect("/userdb")
    return render_template("Signup.html")