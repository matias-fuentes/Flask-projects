import requests

from os import environ
from re import fullmatch
from pathlib import Path
from bson import ObjectId
from functools import wraps
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from dotenv import load_dotenv, find_dotenv
from typing import TypedDict, Union, Optional
from werkzeug.security import check_password_hash
from werkzeug.wrappers import Response as RedirectResponse
from flask import redirect, render_template, request, session
from firebase import initialize_app

load_dotenv(find_dotenv())
spoonacularAPIKey: Optional[str] = environ.get("SPOONACULAR_API_KEY")


def searchPost() -> Union[RedirectResponse, None]:
    query: str = request.form.get("search")
    if query:
        return redirect(f"/articles?q={query}")
    else:
        return None


# Decorate routes to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("loginId") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def getLoginId(sessionLoginId):
    loginId = None
    if sessionLoginId:
        loginId = ObjectId(sessionLoginId)

    return loginId


def getDbTable(connection, table: str):
    db = connection["wikifood"]
    table = db[table]
    return table


def getUsername(usersTable, loginId):
    username = usersTable.find_one({"_id": loginId}, {"username": 1, "_id": 0})[
        "username"
    ]

    return username


# Smartly recognizes whether the user has tried to log in with either his username or his
# email, and validates the login
def isValidLogin(user, password, regExs, session):
    usernameOrEmail = None

    # Before consulting anything, it first checks whether the username or email have the
    # correct syntax or not
    if fullmatch(regExs["username"], user) and len(user) >= 2 and len(user) <= 16:
        usernameOrEmail = "username"
    elif fullmatch(regExs["email"], user) and len(user) >= 2 and len(user) <= 64:
        usernameOrEmail = "email"
    else:
        return {"isValidLogin": False, "usernameOrEmail": "username"}

    invalidResponse = {"isValidLogin": False, "usernameOrEmail": usernameOrEmail}

    # Again, before consulting anything, the code first checks whether the password have
    # the correct syntax or not
    if fullmatch(regExs["password"], password):
        # Now that we know that the syntax for both username/email and password are
        # valid, we first consult with the database to find out whether the user exists
        # or not
        connection = MongoClient(environ.get("MONGODB_URI"))
        usersTable = getDbTable(connection, "users")
        userExists = usersTable.find_one({f"{usernameOrEmail}": user}, {"hash": 1})

        # If it exists, we compare the password that the user provided with the hashed
        # password stored in the database
        if userExists:
            hashedPassword: str = userExists["hash"]
            isValidPassword: bool = check_password_hash(hashedPassword, password)

            # If the password that the user provided it's the same as the hashed password
            # that we have stored in the database, then we log in the user, and return a
            # valid response
            if isValidPassword:
                session["loginId"] = str(userExists["_id"])
                connection.close()

                response = {"isValidLogin": True}
                return response

            # If any of previous checks fails, then we return an invalid response
            else:
                return invalidResponse
        else:
            return invalidResponse
    else:
        return invalidResponse


apiDomain: str = "https://api.spoonacular.com"


# # Make queries to search at the API
def query(search: str) -> dict:
    url: str = f"{apiDomain}/recipes/complexSearch?apiKey={spoonacularAPIKey}&query={search}&number=25&addRecipeInformation=true"
    response: dict = requests.get(url).json()

    return response


# # Make queries to get information of the API
def getArticle(savedArticlesTable, articleId):
    url = f"{apiDomain}/recipes/{articleId}/information?apiKey={spoonacularAPIKey}&includeNutrition=false"
    article = requests.get(url).json()

    # Sometimes the "recipes/{articleId}/information" Spoonacular API endpoint does not include "image" or "summary" keys in the response.
    # In those cases, we make a call on the "recipes/complexSearch" API endpoint to retrieve and include those remaining values.
    if not "image" in article or not "summary" in article:
        searchEndpointURL: str = f"{apiDomain}/recipes/complexSearch?apiKey={spoonacularAPIKey}&query={article['title']}&number=1"
        searchedArticle = requests.get(searchEndpointURL).json()

        if not "image" in article:
            article["image"] = searchedArticle["results"][0]["image"]

        if not "summary" in article:
            article["summary"] = searchedArticle["results"][0]["summary"]

    loginId = getLoginId(session.get("loginId"))
    if loginId:
        savedArticle: dict = savedArticlesTable.find_one(
            {"articleId": articleId, "userId": loginId}, {"_id": 1}
        )

        if savedArticle:
            article["isSaved"]: bool = True

    if "productMatches" in article["winePairing"]:
        winePrice = float(
            article["winePairing"]["productMatches"][0]["price"].replace("$", "")
        )
        winePrice = "{:.2f}".format(winePrice)
        article["winePairing"]["productMatches"][0]["price"] = winePrice

    return article


def saveArticle(savedArticlesTable, articleId, loginId):
    isSaved = request.form.get("savedArticle")
    article = {"userId": loginId, "articleId": articleId}

    if isSaved == "True":
        savedArticlesTable.delete_one(article)
    else:
        savedArticlesTable.insert_one(article)


# Check if an image has a valid format
def allowedImage(image):
    allowedExtensions = set(["png", "jpg", "jpeg", "bmp", "webp"])
    return "." in image and image.rsplit(".", 1)[1].lower() in allowedExtensions


# Crops profile images to a 1:1 aspect ratio
def cropImage(image):
    width, height = image.size

    if width == height:
        return image

    offset = int(abs(height - width) / 2)

    if width > height:
        image = image.crop([offset, 0, width - offset, height])
    else:
        image = image.crop([0, offset, width, height - offset])
    return image


def getProfileInfo(loginId):
    connection = MongoClient(environ.get("MONGODB_URI"))
    usersTable = getDbTable(connection, "users")
    savedArticlesTable = getDbTable(connection, "savedArticles")

    profileInfo = usersTable.find_one(
        {"_id": loginId}, {"username": 1, "profilePic": 1, "bannerPic": 1, "_id": 0}
    )
    savedArticles = savedArticlesTable.find(
        {"userId": loginId}, {"articleId": 1, "_id": 0}
    )

    savedArticlesIds = []
    for article in savedArticles:
        savedArticlesIds.append(article["articleId"])

    savedArticles = []
    for articleId in savedArticlesIds:
        fullArticle = getArticle(savedArticlesTable, articleId)
        article = {
            "title": fullArticle["title"],
            "image": fullArticle["image"],
            "id": fullArticle["id"],
        }
        savedArticles.append(article)

    profileInfo["savedArticles"] = savedArticles
    return profileInfo


class ProfileImages(TypedDict):
    profilePic: str
    bannerPic: str


# Saves images (banner and profile pictures), keeps a record of the images of each image of each user,
# and updates the uploaded images
def uploadImage(profilePic, bannerPic, username, connection, loginId):
    # Firebase Storage configuration object
    config = {
        "apiKey": environ.get("FIREBASE_API_KEY"),
        "authDomain": environ.get("AUTH_DOMAIN"),
        "databaseURL": environ.get("DATABASE_URL"),
        "projectId": environ.get("PROJECT_ID"),
        "storageBucket": environ.get("STORAGE_BUCKET"),
        "messagingSenderId": environ.get("MESSAGING_SENDER_ID"),
        "appId": environ.get("APP_ID"),
        "measurementId": environ.get("MEASUREMENT_ID"),
        "type": environ.get("TYPE"),
        "projectId": environ.get("PROJECT_ID"),
        "privateKeyId": environ.get("PRIVATE_KEY_ID"),
        "privateKey": environ.get("PRIVATE_KEY"),
        "clientEmail": environ.get("CLIENT_EMAIL"),
        "clientId": environ.get("CLIENT_ID"),
        "authUri": environ.get("AUTH_URI"),
        "tokenUri": environ.get("TOKEN_URI"),
        "authProviderX509CertURL": environ.get("AUTH_PROVIDER_X509_CERT_URL"),
        "clientX509CertURL": environ.get("CLIENT_X509_CERT_URL"),
        "universeDomain": environ.get("UNIVERSE_DOMAIN"),
    }

    # Initializing Firebase app
    firebaseApp = initialize_app(config)
    storage = firebaseApp.storage()

    successfulMessage = "The image has been uploaded successfully!"
    errorMessage = "Allowed image types are: png, jpg, jpeg, webp, and bmp."

    profileInfo = getProfileInfo(loginId)
    usersTable = getDbTable(connection, "users")
    if profilePic and bannerPic:
        if allowedImage(profilePic.filename) and allowedImage(bannerPic.filename):
            profilePic.filename = secure_filename(
                str(Path(profilePic.filename).with_suffix(".webp"))
            )
            bannerPic.filename = secure_filename(
                str(Path(bannerPic.filename).with_suffix(".webp"))
            )

            storage.child(profilePic.filename).put(profilePic.read())
            storage.child(bannerPic.filename).put(bannerPic.read())

            profilePic.close()
            bannerPic.close()

            updatedValue = {
                "profilePic": profilePic.filename,
                "bannerPic": bannerPic.filename,
            }
            usersTable.update_one({"username": username}, {"$set": updatedValue}, True)
            connection.close()

            return render_template(
                "profile.html",
                successfulMessage=successfulMessage,
                profileInfo=profileInfo,
                loginId=loginId,
            )

        else:
            return render_template(
                "profile.html",
                errorMessage=errorMessage,
                profileInfo=profileInfo,
                loginId=loginId,
            )

    elif profilePic:
        if allowedImage(profilePic.filename):
            profilePic.filename = secure_filename(
                str(Path(profilePic.filename).with_suffix(".webp"))
            )

            storage.child(profilePic.filename).put(profilePic.read())
            profilePic.close()

            usersTable.update_one(
                {"username": username},
                {"$set": {"profilePic": profilePic.filename}},
                True,
            )
            connection.close()

            return render_template(
                "profile.html",
                successfulMessage=successfulMessage,
                profileInfo=profileInfo,
                loginId=loginId,
            )

        else:
            return render_template(
                "profile.html",
                errorMessage=errorMessage,
                profileInfo=profileInfo,
                loginId=loginId,
            )

    else:
        if allowedImage(bannerPic.filename):
            bannerPic.filename = secure_filename(
                str(Path(bannerPic.filename).with_suffix(".webp"))
            )

            storage.child(bannerPic.filename).put(bannerPic.read())
            bannerPic.close()

            usersTable.update_one(
                {"username": username}, {"$set": {"bannerPic": bannerPic.filename}}
            )
            connection.close()

            return render_template(
                "profile.html",
                successfulMessage=successfulMessage,
                profileInfo=profileInfo,
                loginId=loginId,
            )

        else:
            return render_template(
                "profile.html",
                errorMessage=errorMessage,
                profileInfo=profileInfo,
                loginId=loginId,
            )


# # With this loop we can extract the article ID from the URL. Example:
# # URL: 'https://.../articles/pizza-bites-with-pumpkin-19234984'
# # Article ID extracted: 19234984
def getArticleId(articleURL):
    startPoint = 0
    for i in range(len(articleURL) - 1, -1, -1):
        if articleURL[i] == "-":
            startPoint = i + 1
            break

    articleId = articleURL[startPoint:]
    articleId = int(articleId)
    return articleId
