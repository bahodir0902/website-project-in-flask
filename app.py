import os
from slugify import slugify
from flask import Flask, render_template, request, session, make_response, flash, redirect, url_for
import random
import hashlib

app = Flask(__name__)
app.secret_key = "this_is_a_very_secret"

pas = "admin"
hashed_password = hashlib.sha512(pas.encode()).hexdigest()
users = {
    "admin": hashed_password
}


def read_title():
    files = os.listdir("articles")
    slug_articles = {}
    for file in files:
        #title, _ = os.path.splitext(file)
        title = file.rsplit('.', 1)[0]
        slug = slugify(title)
        slug_articles[slug] = file
    return slug_articles


def load_content(filename):
    try:
        with open(f"articles/{filename}", 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError as e:
        return str(e), 404
    return content


titles = read_title()


@app.route("/")
def blog():
    return render_template("blog.html", titles=titles)


@app.route("/set-session")
def set_session():
    session["user_id"] = random.randint(0, 1000000)
    return "Your user id is set!"


@app.route("/get-session")
def get_session():
    res = ""
    try:
        res = session['user_id']
    except:
        return "Your user id was not found. Please login or sign up."
    return f"Your user id is: {res}"


@app.route("/first-time")
def first_time():
    if 'seen' not in request.cookies:
        response = make_response("You are first time here")
        response.set_cookie('seen', "1")
        return response
    try:
        seen = int(request.cookies['seen'])
    except:
        seen = 0
    response = make_response(f"I have seen you {seen} times")
    response.set_cookie('seen', str(seen + 1))
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_hashed = hashlib.sha512(password.encode()).hexdigest()
        if username in users and users[username] == password_hashed:
            flash('Logged successfully!', 'success')
        else:
            flash('Invalid username or password', 'danger')


    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    password = ""
    if request.method == 'POST':
        username = request.form.get('username')
        if username in users:
            flash("Username is already taken", 'danger')
            return render_template("register.html")

        if request.form.get('password') == request.form.get('password_second'):
            password = request.form.get('password')
        else:
            flash("Passwords don't match", 'danger')
            return render_template("register.html")
        email = request.form.get('email')
        password_hashed = hashlib.sha512(password.encode()).hexdigest()

        if username not in users:
            users[username] = password_hashed
        else:
            flash("User already logged", 'danger')

        print(users)
    return render_template('register.html')


@app.route("/blog/<slug>")
def article_func(slug: str):
    filename = titles[slug]
    content = load_content(filename)
    title_name = filename.rsplit('.', 1)[0]
    return render_template("article.html", content=content, title=title_name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4200, debug=True)
