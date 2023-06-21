import os
import pymongo
from dotenv import load_dotenv, find_dotenv
from flask import Flask, redirect, render_template, request

load_dotenv(find_dotenv())

# Configure application & ensure templates are auto-reloaded
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key=os.environ.get('SECRET_KEY')

@app.route("/", methods=["GET", "POST"])
def index():
    connection = pymongo.MongoClient(os.environ.get('MONGODB_URI'))
    db = connection["birthie"]
    table = db["birthdays"]

    if request.method == "POST":
        name = request.form.get("name")
        month = int(request.form.get("months"))
        day = int(request.form.get("days"))

        birthday = {
            "name": name,
            "month": month,
            "day": day
        }

        table.insert_one(birthday)
        connection.close()
        return redirect("/")
    else:
        birthdays = []
        for document in table.find():
            birthdays.append(document)

        connection.close()
        return render_template("index.html", birthdays=birthdays)
        