import requests
import os
import pyrebase

from webptools import cwebp
from PIL import Image
from re import fullmatch
from flask import redirect, render_template, request, session
from functools import wraps
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

envVars = os.environ
apiKey = envVars.get('apiKey')

# Makes it necessary to log in to enter to the specified page
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Recognizes if you're trying to log in with your username or your email, and ends up logging in if the credentials are valid
def userOrEmail(email, user, password, passRegEx, session, cursor, connection):
    condition = 'email' if email == True else 'username'
    userDB = cursor.execute(
        f"SELECT id, hash FROM users WHERE {condition} = '{user}'")
    userDB = cursor.fetchall()
    connection.close()

    if userDB:
        # Check if password is valid or not
        if not fullmatch(passRegEx, password):
            return render_template("login.html", error=True)

        checkPassword = check_password_hash(userDB[0][1], password)
        if checkPassword:
            session["user_id"] = userDB[0][0]
            return redirect("/")

    return render_template("login.html", error=True)


apiDomain = 'https://api.spoonacular.com'

# Make queries to search at the API
def query(q):
    url = f'{apiDomain}/food/search?apiKey={apiKey}&query={q}'
    response = requests.get(url).json()['searchResults']

    for i in response:
        if ' ' in i['name']:
            i['name'] = i['name'].replace(' ', '-')

    return response


# Make queries to get information of the API
def article(articleType, cursor, articleId):
    if articleType == 'R':
        url = f'{apiDomain}/recipes/{articleId}/information?apiKey={apiKey}'
    elif articleType == 'P':
        url = f'{apiDomain}/food/products/{articleId}?apiKey={apiKey}'
    else:
        url = f'{apiDomain}/food/menuItems/{articleId}?apiKey={apiKey}'

    response = requests.get(url).json()
    logIn = session.get("user_id")
    savedArticle = cursor.execute(
        f"SELECT articleType FROM savedArticles WHERE articleId = '{articleId}' AND userId = '{logIn}'")
    savedArticle = cursor.fetchall()
    getArticle = [response, savedArticle, articleId]
    return getArticle


def saveArticle(cursor, username, articleType, connection):
    if session.get("user_id"):
        articleId = request.args.get('articleId')
        savedArticle = request.form.get('savedArticle')
        logIn = session.get("user_id")
        if savedArticle == 'True':
            cursor.execute(
                f"DELETE FROM savedArticles WHERE userId = '{logIn}' AND articleId = '{articleId}'")
            connection.commit()
        else:
            cursor.execute(
                f"INSERT INTO savedArticles (userId, articleType, articleId) VALUES ('{logIn}', '{articleType}', '{articleId}')")
            connection.commit()

        getArticle = article(articleType, cursor, articleId)
        connection.close()
        return render_template("article.html", getArticle=getArticle, articleType=articleType, logIn=logIn, username=username)

    return redirect("/login")


def searchPost():
    search = request.form.get("search")
    return redirect(f"/search?q={search}")


# Check if an image has a valid format
def allowedImage(image):
    allowedExtensions = set(['png', 'jpg', 'jpeg', 'bmp', 'webp'])
    return '.' in image and image.rsplit('.', 1)[1].lower() in allowedExtensions


# Crops profile images to an 1:1 aspect ratio
def cropImage(image):
    width, height = image.size
    if width == height:
        return image
    offset = int(abs(height-width)/2)
    if width > height:
        image = image.crop([offset, 0, width-offset, height])
    else:
        image = image.crop([0, offset, width, height-offset])
    return image


# Saves images (banner and profile pictures), keeps a record of the images of each image of each user, and updates the uploaded images
def uploadImage(cursor, profilePic, bannerPic, username, connection, logIn):
    config = {
        "apiKey": envVars.get('firebaseApiKey'),
        "authDomain": envVars.get('authDomain'),
        "projectId": envVars.get('projectId'),
        "storageBucket": envVars.get('storageBucket'),
        "messagingSenderId": envVars.get('messagingSenderId'),
        "appId": envVars.get('appId'),
        "measurementId": envVars.get('measurementId'),
        "serviceAccount": {
                "type": envVars.get('type'),
                "project_id": envVars.get('projectId'),
                "private_key_id": envVars.get('privateKeyId'),
                "private_key": envVars.get('privateKey').replace('\\n', '\n'),
                "client_email": envVars.get('clientEmail'),
                "client_id": envVars.get('clientId'),
                "auth_uri": envVars.get('authUri'),
                "token_uri": envVars.get('tokenUri'),
                "auth_provider_x509_cert_url": envVars.get('authProviderx509CertURL'),
                "client_x509_cert_url": envVars.get('clientx509CertURL')
            },
        "databaseURL": envVars.get('databaseURL')
    }

    firebase = pyrebase.initialize_app(config)
    storage = firebase.storage()
    profilePicDir = 'static/temp/profilePictures/'
    bannerPicDir = 'static/temp/bannerPictures/'

    if profilePic and bannerPic:
        if allowedImage(profilePic.filename) and allowedImage(bannerPic.filename):
            profFilename = secure_filename(profilePic.filename)
            bannFilename = secure_filename(bannerPic.filename)

            image = Image.open(profilePic)
            profilePic = cropImage(image)

            profilePic.save(os.path.join(profilePicDir, profFilename))
            bannerPic.save(os.path.join(bannerPicDir, bannFilename))

            formatIndex = profFilename.find(
                '.', len(profFilename) - 5, len(profFilename) - 1)
            profFilenameWebp = profFilename[:formatIndex] + '.webp'
            formatIndex = bannFilename.find(
                '.', len(bannFilename) - 5, len(bannFilename) - 1)
            bannFilenameWebp = bannFilename[:formatIndex] + '.webp'

            cwebp(input_image=profilePicDir + profFilename,
                  output_image=profilePicDir + profFilenameWebp, option='-q 80')
            cwebp(input_image=bannerPicDir + bannFilename,
                  output_image=bannerPicDir + bannFilenameWebp, option='-q 80')

            storage.child(profFilenameWebp).put(
                profilePicDir + profFilenameWebp)
            storage.child(bannFilenameWebp).put(
                bannerPicDir + bannFilenameWebp)

            cursor.execute(
                f"UPDATE users SET profilePicDir = '{profFilenameWebp}', bannerPicDir = '{bannFilenameWebp}' WHERE username = '{username}'")
            connection.commit()

            os.remove(profilePicDir + profFilename)
            os.remove(profilePicDir + profFilenameWebp)
            os.remove(bannerPicDir + bannFilename)
            os.remove(bannerPicDir + bannFilenameWebp)

            picDirectory, articles = getProfInfo(cursor, logIn)
            connection.close()
            successfulMessage = 'The images have been uploaded successfully. You\'ll see the changes in a few minutes.'

            return render_template("profile.html", successfulMessage=successfulMessage, picDirectory=picDirectory,
                                   logIn=session.get("user_id"), username=username, articles=articles)

        else:
            errorMessage = 'Allowed image types are: png, jpg, jpeg, webp, and bmp.'
            return render_template("profile.html", errorMessage=errorMessage, logIn=session.get("user_id"), username=username)

    elif profilePic:
        if allowedImage(profilePic.filename):
            profFilename = secure_filename(profilePic.filename)

            image = Image.open(profilePic)
            profilePic = cropImage(image)
            profilePic.save(os.path.join(profilePicDir, profFilename))

            formatIndex = profFilename.find(
                '.', len(profFilename) - 5, len(profFilename) - 1)
            profFilenameWebp = profFilename[:formatIndex] + '.webp'

            cwebp(input_image=profilePicDir + profFilename,
                  output_image=profilePicDir + profFilenameWebp, option='-q 80')
            storage.child(profFilenameWebp).put(
                profilePicDir + profFilenameWebp)

            cursor.execute(
                f"UPDATE users SET profilePicDir = '{profFilenameWebp}' WHERE username = '{username}'")
            connection.commit()
            picDirectory, articles = getProfInfo(cursor, logIn)
            connection.close()
            successfulMessage = 'The image has been uploaded successfully. You\'ll see the changes in a few minutes.'

            return render_template("profile.html", successfulMessage=successfulMessage, picDirectory=picDirectory,
                                   logIn=session.get("user_id"), username=username, articles=articles)

        else:
            errorMessage = 'Allowed image types are - png, jpg, jpeg, webp, and bmp'
            return render_template("profile.html", errorMessage=errorMessage, logIn=session.get("user_id"), username=username)

    else:
        if allowedImage(bannerPic.filename):
            bannFilename = secure_filename(bannerPic.filename)
            bannerPic.save(os.path.join(bannerPicDir, bannFilename))

            formatIndex = bannFilename.find(
                '.', len(bannFilename) - 5, len(bannFilename) - 1)
            bannFilenameWebp = bannFilename[:formatIndex] + '.webp'

            cwebp(input_image=bannerPicDir + bannFilename,
                  output_image=bannerPicDir + bannFilenameWebp, option='-q 80')
            storage.child(bannFilenameWebp).put(
                bannerPicDir + bannFilenameWebp)

            cursor.execute(
                f"UPDATE users SET bannerPicDir = '{bannFilenameWebp}' WHERE username = '{username}'")
            connection.commit()
            picDirectory, articles = getProfInfo(cursor, logIn)
            connection.close()
            successfulMessage = 'The image has been uploaded successfully. You\'ll see the changes in a few minutes.'

            return render_template("profile.html", successfulMessage=successfulMessage, picDirectory=picDirectory,
                                   logIn=session.get("user_id"), username=username, articles=articles)

        else:
            errorMessage = 'Allowed image types are - png, jpg, jpeg, webp, and bmp'
            return render_template("profile.html", errorMessage=errorMessage, logIn=session.get("user_id"), username=username)


def getUsername(cursor):
    logIn = session.get("user_id")
    if logIn:
        username = cursor.execute(
            f"SELECT username FROM users WHERE id = '{logIn}'")
        username = cursor.fetchone()[0]
    else:
        username = None

    return username


def getProfInfo(cursor, logIn):
    # Make another separately query to get the saved articles information
    picDirectory = cursor.execute(
        f"SELECT profilePicDir, bannerPicDir FROM users WHERE id = '{logIn}'")
    picDirectory = cursor.fetchall()
    savedArticles = cursor.execute(
        f"SELECT articleType, articleId FROM savedArticles WHERE userId = '{logIn}'")
    savedArticles = cursor.fetchall()

    articles = []
    for i in savedArticles:
        articles.append(article(i[0], cursor, i[1]))

    return picDirectory, articles