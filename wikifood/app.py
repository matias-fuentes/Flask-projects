import mysql.connector.pooling
import os

envVars = os.environ
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name=envVars.get('poolName'),
    pool_reset_session=True,
    pool_size=4,
    host=envVars.get('host'),
    port=envVars.get('port'),
    user=envVars.get('user'),
    password=envVars.get('password'),
    db=envVars.get('db')
)

from re import fullmatch
from helpers import login_required, userOrEmail, query, article, saveArticle, searchPost, uploadImage, getUsername, getProfInfo
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key=envVars.get('secretKey')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# RegExs to validate inputs
userRegEx = '[A-Za-z0-9._-]{3,16}'
emailRegEx = '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
passRegEx = '[A-Za-z0-9¡!¿?$+._-]{6,16}'

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return searchPost()

    connection = pool.get_connection()
    cursor = connection.cursor()
    username=getUsername(cursor)
    connection.close()

    return render_template("index.html", index=True, logIn=session.get("user_id"), username=username)


@app.route("/search", methods=["GET", "POST"])
def search():
    connection = pool.get_connection()
    cursor = connection.cursor()

    username = getUsername(cursor)
    connection.close()
    if request.method == "POST":
        return searchPost()

    q = request.args.get('q')
    response = query(q)
    return render_template("search.html", response=response, logIn=session.get("user_id"), username=username)


@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    connection = pool.get_connection()
    cursor = connection.cursor()
    username = getUsername(cursor)

    if request.method == "POST":
        search = request.form.get('search')
        if search:
            return searchPost()

        return saveArticle(cursor, username, 'R', connection)

    articleId = request.args.get('articleId')
    getArticle = article('R', cursor, articleId)
    connection.close()
    return render_template("article.html", getArticle=getArticle, articleType='R', logIn=session.get("user_id"), username=username)


@app.route("/products", methods=["GET", "POST"])
def products():
    connection = pool.get_connection()
    cursor = connection.cursor()
    username = getUsername(cursor)
    if request.method == "POST":
        search = request.form.get('search')
        if search:
            return searchPost()

        return saveArticle(cursor, username, 'P', connection)

    articleId = request.args.get('articleId')
    getArticle = article('P', cursor, articleId)
    connection.close()
    return render_template("article.html", getArticle=getArticle, articleType='P', logIn=session.get("user_id"), username=username)


@app.route("/menu-items", methods=["GET", "POST"])
def menuItems():
    connection = pool.get_connection()
    cursor = connection.cursor()
    username = getUsername(cursor)
    if request.method == "POST":
        search = request.form.get('search')
        if search:
            return searchPost()

        return saveArticle(cursor, username, 'M', connection)

    articleId = request.args.get('articleId')
    getArticle = article('M', cursor, articleId)
    connection.close()
    return render_template("article.html", getArticle=getArticle, articleType='M', logIn=session.get("user_id"), username=username)


@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        search = request.form.get("search")
        if search:
            return redirect(f"/search?q={search}")

        username = request.form.get("username")
        email = request.form.get("email").lower()
        password = request.form.get("password")
        confirmPassword = request.form.get("confirm-password")

        # Check if username is valid or not
        if not fullmatch(userRegEx, username):
            if len(username) < 3 or len(username) > 16:
                errorMessage = 'Username must be at least 3 characters, with a maximum of 16 characters.'
                return render_template("register.html", errorMessage=errorMessage)

            errorMessage = 'Invalid username. Please, use valid special characters (underscore, minus, and periods).'
            return render_template('register.html', errorMessage=errorMessage)

        elif len(email) < 6 or len(email) > 64:
            errorMessage = 'Email must be at least 6 characters, with a maximum of 64 characters.'
            return render_template("register.html", errorMessage=errorMessage)

        # Check if email is valid or not
        elif not fullmatch(emailRegEx, email):
            errorMessage = 'Invalid email. Please, try again.'
            return render_template("register.html", errorMessage=errorMessage)

        elif password != confirmPassword:
            errorMessage = 'Password and confirmation does not match. Please, try again.'
            return render_template("register.html", errorMessage=errorMessage)

        # Check if password is valid or not
        elif not fullmatch(passRegEx, password):
            if len(password) < 6 or len(password) > 16:
                errorMessage = 'Password must be at least 6 characters, with a maximum of 16 characters.'
                return render_template("register.html", errorMessage=errorMessage)

            errorMessage = 'Invalid password. Please, use valid special characters.'
            return render_template("register.html", errorMessage=errorMessage)

        # Check both if username or password have two or more consecutive periods
        elif '..' in username or '..' in password:
            errorMessage = 'Username and password cannot contain two or more consecutive periods (.).'
            return render_template("register.html", errorMessage=errorMessage)

        # Check both if username and/or password already exists. If not, then the account is created
        else:
            connection = pool.get_connection()
            cursor = connection.cursor()

            exists = cursor.execute(f"SELECT username FROM users WHERE username = '{username}'")
            exists = cursor.fetchone()
            if exists:
                errorMessage = 'The username is already taken. Please, try again.'
                return render_template("register.html", errorMessage=errorMessage)

            exists = cursor.execute(f"SELECT email FROM users WHERE email = '{email}'")
            exists = cursor.fetchone()
            if exists:
                errorMessage = 'The email is already in use. Please, try again, or '
                return render_template("register.html", errorMessage=errorMessage, emailExists=True)

            hashedPassword = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

            cursor.execute(f"INSERT INTO users (username, email, hash) VALUES ('{username}', '{email}', '{hashedPassword}')")
            connection.commit()
            userId = cursor.execute(f"SELECT id FROM users WHERE username = '{username}'")
            userId = cursor.fetchone()
            connection.close()
            session["user_id"] = userId[0]

            return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        search = request.form.get("search")
        if search:
            return redirect(f"/search?q={search}")

        user = request.form.get("user")
        password = request.form.get("password")

        # We can log in either with our username or with our email.
        # If there's an '@' in user, that means that we're dealing with an email.
        if '@' in user:
            user = user.lower()

            if len(user) < 6 or len(user) > 64:
                return render_template("login.html", error=True)

            elif not fullmatch(emailRegEx, user):
                return render_template("login.html", error=True)

            connection = pool.get_connection()
            cursor = connection.cursor()

            return userOrEmail(True, user, password, passRegEx, session, cursor, connection)

        elif not fullmatch(userRegEx, user):
            return render_template("login.html", error=True)

        connection = pool.get_connection()
        cursor = connection.cursor()

        return userOrEmail(False, user, password, passRegEx, session, cursor, connection)

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    connection = pool.get_connection()
    cursor = connection.cursor()

    username = getUsername(cursor)
    logIn = session.get("user_id")
    if request.method == "POST":
        search = request.form.get("search")
        if search:
            return redirect(f"/search?q={search}")

        profilePic = request.files['profilePic']
        bannerPic = request.files['bannerPic']
        if profilePic or bannerPic:
            return uploadImage(cursor, profilePic, bannerPic, username, connection, logIn)

    picDirectory, articles = getProfInfo(cursor, logIn)
    connection.close()
    return render_template("profile.html", picDirectory=picDirectory, username=username, logIn=logIn, articles=articles)