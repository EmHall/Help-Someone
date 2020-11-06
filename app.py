import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/", methods=["GET", "POST"])
@app.route("/help")
def get_help():
    help = list(mongo.db.categories.find())
    people = list(mongo.db.recipients.find())
    if request.method=="POST":
        print("I'm in")
        name = request.form['task_name']
        email = request.form['email']
        task_description = request.form['task_description']
        category_db=mongo.db.categories
        category_db.insert_one({
            'task_name': name,
            'email': email,
            'task_description': task_description,
            'category': 'exam'
        })
    return render_template("help.html", help=help, people=people)
    

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        session["logged_in"] = True
        flash("Registration Successful!")
        return redirect(url_for("get_help", username=session["user"]))

    return render_template("help.html")


# !/usr/bin/python
# -*- coding: utf-8 -*-


# !/usr/bin/python
# -*- coding: utf-8 -*-


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        # check if username exists in db

        existing_user = mongo.db.users.find_one({'username': request.form.get('username').lower()})

        if existing_user:

            # ensure hashed password matches user input

            if check_password_hash(existing_user['password'],
                                   request.form.get('password')):
                session['user'] = request.form.get('username').lower()
                session['logged_in'] = True
                flash('Welcome, {}'.format(request.form.get('username')))
                return redirect(url_for('profile',
                                username=session['user']))
            else:

                # invalid password match

                flash('Incorrect Username and/or Password')
                return redirect(url_for('help'))
        else:

            # username doesn't exist

            flash('Incorrect Username and/or Password')
            return redirect(url_for('help'))

    return render_template('help.html')


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("help.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.clear()
    return redirect(url_for("login"))


@app.route("/add_help")
def add_help():
    return render_template("add_help.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
