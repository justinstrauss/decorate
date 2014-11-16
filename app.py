# Justin Strauss and Derek Tsui
# Software Development Period 7
# MongoDB Project

import db
from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for, flash

app = Flask(__name__)

def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if session["name"]==None:
            flash("You must login to access this protected page!")
            session['nextpage'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return inner

def authenticate(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            #if authenticate(username,password):
            if db.authenticate(username,password):
                session['name'] = username
                page = session.pop('nextpage','/')
                return redirect(page)
            else:
                if db.userexists(username):
                    flash("You've inputted the wrong password for the given user.")
                    return redirect(url_for('login'))
                else:
                    flash("The username you inputted hasn't been registered yet.")
                    return redirect(url_for('register'))
        return f(*args, **kwargs)    
    return inner

@app.route('/', methods=["POST","GET"])
@app.route('/index', methods=["POST","GET"])
def index():
    if "name" not in session:
        session["name"] = None
    return render_template("index.html")

@app.route("/login", methods=["POST","GET"])
@authenticate
def login():
    return render_template("login.html")

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('name', None)
    return redirect(url_for('index'))

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        pw = request.form["password"]
        pw2 = request.form["password2"]
        if pw != pw2:
            flash("The passwords you submitted don't match, please try again.")
            return redirect(url_for('register'))
        if db.userexists(username):
            flash("The username you submitted is already taken, please try again.")
            return redirect(url_for('register'))
        if db.emailexists(email):
            flash("The email you submitted already has an account tied to it, please try again.")
            return redirect(url_for('register'))
        else:
            db.adduser(username,email,pw)
            flash("You've sucessfully registered, now login!")
            return redirect(url_for('login'))
    else:
        if session['name']!=None:
            flash("You're already logged in, so you can't register for a second account!")
            page = session.pop('nextpage','/')
            return redirect(page)
        return render_template("register.html")

@app.route("/user", methods=["POST","GET"])
@login_required
def myself():
    if request.method == "GET":
        profile=db.getprofile(session['name'])
        #print profile
        posts = db.getposts(session['name'])
        return render_template("profile.html",profile=profile, posts=posts)
    else:
        newpw = request.form["newpassword"]
        newpw2 = request.form["newpassword2"]
        if (newpw != newpw2):
            flash("The new passwords you submitted don't match, please try again.")
            return redirect(url_for('myself'))
        else:
            db.updatepw(session['name'],newpw)
            flash("Your password has been sucessfully changed. Please re-login.")
            return redirect(url_for('logout'))

@app.route("/user/<username>")
@login_required
def user(username):
    profile=db.getprofile(username)
    #print profile
    posts = db.getposts(username)
    return render_template("profileother.html",profile=profile,posts=posts)

@app.route("/blog", methods=["POST","GET"])
@login_required
def blog():
    if request.method == "GET":
        blog=db.getblog(session['name'])
        print blog
        return render_template("blog.html",blog=blog)
    else:
        title = request.form["title"]
        content = request.form["content"]
        if db.invalidpost(title, content):
            flash("A post of this title already exists or there is no content!")
            return redirect(url_for('blog'))
        else:
            db.addpost(title,session['name'],content)
            flash("You have successfully made a blog post!")
            return redirect(url_for('blog'))

@app.route("/blog/<title>", methods=["POST","GET"])
@login_required
def blogcontent(title):
    if request.method == "GET":
        blogcontent=db.getblogcontent(title)
        print blogcontent
        return render_template("blogcontent.html",title=title,blogcontent=blogcontent)
    else:
        comment = request.form["comment"]
        if db.invalidcomment(comment):
            flash("There is no text in your comment!")
            return redirect(url_for('blog'))
        else:
            db.addcomment(title,session['name'],comment)
            flash("You have successfully made a comment!")
            return redirect(url_for('blog'))

@app.route("/blog/upvote/<title>", methods=["POST","GET"])
@login_required
def upvote(title):
    db.votepost(title,1)
    return redirect(url_for('blog'))

@app.route("/blog/downvote/<title>", methods=["POST","GET"])
@login_required
def downvote(title):
    db.votepost(title,-1)
    return redirect(url_for('blog'))

@app.route("/contacts")
@login_required
def contacts():
    contacts=db.getcontacts(session['name'])
    print contacts
    return render_template("contacts.html",contacts=contacts)

if __name__ == '__main__':
    db.setup()
    app.secret_key = "don't store this on github"
    app.debug = True
    app.run(host='0.0.0.0')
