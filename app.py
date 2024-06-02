import os
from slugify import slugify
from flask import Flask, render_template, request, session, make_response, flash, redirect, url_for
import random
import hashlib
import psycopg2

connect_users = psycopg2.connect(
    host="localhost",
    database="contacts",
    user="postgres",
    password="Bahodir2005"
)

cloud = psycopg2.connect(
    "postgresql://Fikrlog_users_owner:zREM0lZt3kxh@ep-red-art-a278gyy5.eu-central-1.aws.neon.tech/Fikrlog_users?sslmode=require")

app = Flask(__name__)
app.secret_key = "this_is_a_very_secret"
cur = connect_users.cursor()
instructor = cloud.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, 
            first_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, 
            password TEXT NOT NULL)"""
            )

instructor.execute("""CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, 
                   first_name TEXT NOT NULL,
                   email TEXT UNIQUE NOT NULL, 
                   password TEXT NOT NULL)"""
                   )
instructor.execute("COMMIT")

def read_title():
    files = os.listdir("articles")
    slug_articles = {}
    for file in files:
        # title, _ = os.path.splitext(file)
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
        user_or_email = request.form.get('user_or_email')
        password = request.form.get('password')
        password_hashed = hashlib.sha512(password.encode()).hexdigest()

        instructor.execute("SELECT * FROM Users WHERE email= %s OR first_name= %s", (user_or_email, user_or_email))
        user_from_database = instructor.fetchone()

        if user_from_database is not None and user_from_database[3] == password_hashed:
            flash('Logged successfully!', 'success')
        else:
            flash('Invalid username or password', 'danger')

    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    password = ""
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')

        if request.form.get('password') == request.form.get('password_second'):
            password = request.form.get('password')
        else:
            flash("Passwords don't match", 'danger')
            return render_template("register.html")

        password_hashed = hashlib.sha512(password.encode()).hexdigest()

        instructor.execute("SELECT * FROM Users WHERE email= %s", (email,))
        email_from_database = instructor.fetchone()

        if email_from_database is None:
            cur.execute("INSERT INTO Users(first_name,email,password) VALUES(%s, %s, %s)",
                        (username, email, password_hashed))
            connect_users.commit()

            instructor.execute("INSERT INTO Users(first_name,email,password) VALUES(%s, %s, %s)",
                        (username, email, password_hashed))
            instructor.execute("COMMIT")

        else:
            flash("User already exists", 'danger')

    return render_template('register.html')


@app.route("/blog/<slug>")
def article_func(slug: str):
    filename = titles[slug]
    content = load_content(filename)
    title_name = filename.rsplit('.', 1)[0]
    return render_template("article.html", content=content, title=title_name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4200, debug=True)
