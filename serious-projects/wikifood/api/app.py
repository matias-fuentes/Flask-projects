from os import environ
from re import fullmatch
from pymongo import MongoClient
from typing import Union
from dotenv import load_dotenv, find_dotenv
from werkzeug.security import generate_password_hash
from werkzeug.wrappers import Response as RedirectResponse
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    Response as FlaskResponse,
    Markup,
)
from api.helpers import (
    searchPost,
    login_required,
    getLoginId,
    isValidLogin,
    query,
    getArticle,
    saveArticle,
    uploadImage,
    getDbTable,
    getArticleId,
    getProfileInfo,
)

load_dotenv(find_dotenv())
app: Flask = Flask(__name__)
app.secret_key = environ.get("SECRET_KEY")

# # Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# # Configure upload settings
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# # Type aliases
SearchPostResponse = Union[RedirectResponse, None]


# Ensure responses aren't cached
@app.after_request
def after_request(response: FlaskResponse) -> FlaskResponse:
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return searchPost()

    loginId = getLoginId(session.get("loginId"))
    return render_template("index.html", index=True, loginId=loginId)


@app.route("/articles", methods=["GET", "POST"])
def searchArticles() -> Union[SearchPostResponse, str]:
    if request.method == "POST":
        return searchPost()

    # Handle empty state if there is no query param on the URL
    search: str = request.args.get("q")
    loginId = getLoginId(session.get("loginId"))

    if not search:
        return render_template("search.html", emptyState=True, loginId=loginId)

    response: dict = query(search)
    if response:
        for i in response["results"]:
            # Before we convert i["summary"] to HTML with Markup(), we must remove any
            # instance of any anchor tag that it may have, since if we don't, it will
            # break up the HTML since we will be putting an anchor tag (hyperlink of the
            # summary) inside an anchor tag (the recipe card, which redirects you to its
            # respective article), and that's not possible.
            i["summary"].replace("<a>", "")
            i["summary"].replace("</a>", "")
            i["summary"] = Markup(i["summary"])

    return render_template("search.html", response=response, loginId=loginId)


@app.route("/articles/<articleURL>", methods=["GET", "POST"])
def articleId(articleURL):
    # Connect to MongoDB and retrieve the username
    connection = MongoClient(environ.get("MONGODB_URI"))
    savedArticlesTable = getDbTable(connection, "savedArticles")

    articleId = getArticleId(articleURL)
    article = getArticle(savedArticlesTable, articleId)
    loginId = getLoginId(session.get("loginId"))

    # Handle POST method if the user searchs someting on the search bar, or if he saves the article
    if request.method == "POST":
        search = request.form.get("search")

        if search:
            connection.close()
            return searchPost()
        if loginId:
            saveArticle(savedArticlesTable, articleId, loginId)
            connection.close()

            successfulMessage = "Changes saved successfully! You'll see the changes in a couple of seconds."
            return render_template(
                "article.html",
                article=article,
                loginId=loginId,
                successfulMessage=successfulMessage,
            )
        else:
            connection.close()
            return redirect("/login")

    connection.close()
    return render_template("article.html", article=article, loginId=loginId)


# RegExs to validate inputs
userRegEx = "[A-Za-z0-9._-]{3,16}"
emailRegEx = "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"
passwordRegEx = "[A-Za-z0-9¡!¿?$+._-]{6,16}"


@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Forget any loginId
    session.clear()

    if request.method == "POST":
        search = request.form.get("search")

        if search:
            return redirect(f"/articles?q={search}")

        username = request.form.get("username")
        email = request.form.get("email").lower()
        password = request.form.get("password")
        confirmedPassword = request.form.get("confirmed-password")

        # Check if username is valid or not
        if not fullmatch(userRegEx, username):
            if len(username) < 3 or len(username) > 16:
                errorMessage = "Username must be at least 3 characters, with a maximum of 16 characters."
                return render_template("signup.html", errorMessage=errorMessage)

            errorMessage = "Invalid username. Please, use valid special characters (underscore, minus, and periods)."
            return render_template("signup.html", errorMessage=errorMessage)

        elif len(email) < 6 or len(email) > 64:
            errorMessage = (
                "Email must be at least 6 characters, with a maximum of 64 characters."
            )
            return render_template("signup.html", errorMessage=errorMessage)

        # Check if email is valid or not
        elif not fullmatch(emailRegEx, email):
            errorMessage = "Invalid email. Please, try again."
            return render_template("signup.html", errorMessage=errorMessage)

        elif password != confirmedPassword:
            errorMessage = (
                "Password and confirmation does not match. Please, try again."
            )
            return render_template("signup.html", errorMessage=errorMessage)

        # Check if password is valid or not
        elif not fullmatch(passwordRegEx, password):
            if len(password) < 6 or len(password) > 16:
                errorMessage = "Password must be at least 6 characters, with a maximum of 16 characters."
                return render_template("signup.html", errorMessage=errorMessage)

            errorMessage = "Invalid password. Please, use valid special characters."
            return render_template("signup.html", errorMessage=errorMessage)

        # Check both if username or password have two or more consecutive periods
        elif ".." in username or ".." in password:
            errorMessage = "Username and password cannot contain two or more consecutive periods (.)."
            return render_template("signup.html", errorMessage=errorMessage)

        # Check both if username and/or password already exists. If not, then the account
        # is created
        else:
            connection = MongoClient(environ.get("MONGODB_URI"))
            usersTable = getDbTable(connection, "users")

            errorMessage = "The username is already taken. Please, try again or "
            exists = usersTable.find_one(
                {"username": username}, {"username": 1, "_id": 0}
            )

            if exists:
                connection.close()
                return render_template("signup.html", errorMessage=errorMessage)

            exists = usersTable.find_one({"email": email}, {"email": 1, "_id": 0})

            if exists:
                connection.close()
                errorMessage = errorMessage.replace("username", "email")
                return render_template("signup.html", errorMessage=errorMessage)

            hashedPassword = generate_password_hash(
                password, method="pbkdf2:sha256", salt_length=8
            )

            # If everything is correct and has passed all the conditions, then we create
            # the user object that we want to insert on the database, and insert it
            userToInsert = {
                "username": username,
                "email": email,
                "hash": hashedPassword,
            }
            usersTable.insert_one(userToInsert)
            loginId = usersTable.find_one({"username": username}, {"_id": 1})["_id"]
            session["loginId"] = str(loginId)
            connection.close()

            return redirect("/")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Clear session cookies
    session.clear()

    if request.method == "POST":
        search = request.form.get("search")

        if search:
            return redirect(f"/articles?q={search}")

        user = request.form.get("user").lower()
        password = request.form.get("password")
        regExs = {
            "username": userRegEx,
            "email": emailRegEx,
            "password": passwordRegEx,
        }

        response = isValidLogin(user, password, regExs, session)

        if response["isValidLogin"] == False:
            # This code from here modifies the error message depending whether the user
            # has tried to log in with either his username or his email
            errorMessage = (
                "Your username and/or password are incorrect. Please, try again."
            )
            if response["usernameOrEmail"] == "email":
                errorMessage = errorMessage.replace("username", "email")

            return render_template("login.html", errorMessage=errorMessage)
        else:
            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    # Clear session cookies
    session.clear()
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    connection = MongoClient(environ.get("MONGODB_URI"))
    loginId = getLoginId(session.get("loginId"))
    profileInfo = getProfileInfo(loginId)

    if request.method == "POST":
        search = request.form.get("search")

        if search:
            connection.close()
            return redirect(f"/articles?q={search}")

        profilePic = request.files["profilePic"]
        bannerPic = request.files["bannerPic"]
        if profilePic or bannerPic:
            usersTable = getDbTable(connection, "users")
            username = usersTable.find_one({"_id": loginId}, {"username": 1, "_id": 0})[
                "username"
            ]

            return uploadImage(profilePic, bannerPic, username, connection, loginId)

        articleList = request.form.getlist("articles")
        if articleList:
            articleListInt = [eval(article) for article in articleList]
            savedArticlesTable = getDbTable(connection, "savedArticles")
            savedArticlesTable.delete_many(
                {"userId": loginId, "articleId": {"$in": articleListInt}}
            )
            connection.close()

            successfulMessage = "Article(s) deleted successfully! You'll see the changes in a couple of seconds."
            return render_template(
                "profile.html",
                profileInfo=profileInfo,
                loginId=loginId,
                successfulMessage=successfulMessage,
            )

        connection.close()
        return render_template("profile.html", profileInfo=profileInfo, loginId=loginId)

    connection.close()
    return render_template(
        "profile.html",
        profileInfo=profileInfo,
        loginId=loginId,
    )
